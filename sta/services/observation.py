import uuid
import math
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from pydantic.alias_generators import to_camel
from psycopg.errors import UniqueViolation
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.db.utils import IntegrityError
from iam.models import APIKey
from sta.models import Observation
from sta.schemas.observation import (
    ObservationFields,
    ObservationOrderByFields,
    ObservationSummaryResponse,
    ObservationDetailResponse,
    ObservationPostBody,
    ObservationPatchBody,
    ObservationBulkPostBody,
    ObservationBulkDeleteBody,
    ObservationCopyBody,
)
from sta.tasks import copy_observations
from sta.services.datastream import DatastreamService
from api.service import ServiceUtils


User = get_user_model()
datastream_service = DatastreamService()


class ObservationService(ServiceUtils):
    @staticmethod
    def handle_http_404_error(operation, *args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except HttpError as e:
            if e.status_code == 404:
                raise HttpError(400, str(e))
            else:
                raise e

    def get_observation_for_action(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        datastream_id: Optional[uuid.UUID] = None,
        expand_related: Optional[bool] = None,
    ):
        try:
            observation = Observation.objects
            if expand_related:
                observation = self.select_expanded_fields(observation)
            else:
                observation = observation.select_related("datastream__thing")
            if datastream_id:
                observation = observation.get(id=uid, datastream__id=datastream_id)
            else:
                observation = observation.get(id=uid)
        except Observation.DoesNotExist:
            raise HttpError(404, "Observation does not exist")

        observation_permissions = observation.get_principal_permissions(
            principal=principal
        )

        if "view" not in observation_permissions:
            raise HttpError(404, "Observation does not exist")

        if action not in observation_permissions:
            raise HttpError(
                403, f"You do not have permission to {action} this observation"
            )

        return observation

    @staticmethod
    def select_expanded_fields(queryset: QuerySet) -> QuerySet:
        return queryset.select_related(
            "datastream", "datastream__thing", "datastream__thing__workspace"
        )

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        datastream_id: Optional[uuid.UUID] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
        response_format: Optional[str] = None,
        expand_related: Optional[bool] = None,
    ):
        queryset = Observation.objects

        if datastream_id:
            datastream = datastream_service.get_datastream_for_action(
                principal, datastream_id, action="view"
            )
            queryset = queryset.filter(datastream=datastream)

        for field in [
            "phenomenon_time__lte",
            "phenomenon_time__gte",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if not order_by:
            order_by.append("phenomenonTime")

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(ObservationOrderByFields)),
            )

        if expand_related:
            queryset = self.select_expanded_fields(queryset)
        else:
            queryset = queryset.select_related("datastream__thing")

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        if response_format == "row":
            fields = ["phenomenon_time", "result"]
            return {
                "fields": [to_camel(field) for field in fields],
                "data": list(queryset.values_list(*fields)),
            }
        elif response_format == "column":
            fields = ["phenomenon_time", "result"]
            observations = list(queryset.values_list(*fields))
            return (
                dict(zip(fields, zip(*observations)))
                if observations
                else {to_camel(field): [] for field in fields}
            )
        else:
            return [
                (
                    ObservationDetailResponse.model_validate(observation)
                    if expand_related
                    else ObservationSummaryResponse.model_validate(observation)
                )
                for observation in queryset.all()
            ]

    def get(
        self,
        principal: Optional[User | APIKey],
        uid: uuid.UUID,
        datastream_id: Optional[uuid.UUID] = None,
        expand_related: Optional[bool] = None,
    ):
        observation = self.get_observation_for_action(
            principal=principal,
            uid=uid,
            action="view",
            datastream_id=datastream_id,
            expand_related=expand_related,
        )

        return (
            ObservationDetailResponse.model_validate(observation)
            if expand_related
            else ObservationSummaryResponse.model_validate(observation)
        )

    def create(
        self,
        principal: User | APIKey,
        data: ObservationPostBody,
        datastream_id: uuid.UUID,
        expand_related: Optional[bool] = None,
        update_datastream_statistics: bool = True,
    ):
        datastream = datastream_service.get_datastream_for_action(
            principal, datastream_id, action="edit"
        )
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=datastream.thing.workspace_id
        )

        if not Observation.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this observation"
            )

        try:
            observation = Observation.objects.create(
                datastream=datastream,
                **data.dict(include=set(ObservationFields.model_fields.keys())),
            )
        except (
            IntegrityError,
            UniqueViolation,
        ):
            raise HttpError(409, "Duplicate phenomenonTime found on this datastream.")

        if update_datastream_statistics is True:
            datastream_service.update_observation_statistics(
                datastream=datastream,
                fields=["phenomenon_begin_time", "phenomenon_end_time", "value_count"],
            )

        return self.get(
            principal=principal, uid=observation.id, datastream_id=datastream_id
        )

    def update(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        data: ObservationPatchBody,
        datastream_id: Optional[uuid.UUID] = None,
        expand_related: Optional[bool] = None,
        update_datastream_statistics: bool = True,
    ):
        datastream = datastream_service.get_datastream_for_action(
            principal, datastream_id, action="edit"
        )
        observation = self.get_observation_for_action(
            principal=principal,
            uid=uid,
            action="edit",
            expand_related=expand_related,
        )
        observation_data = data.dict(
            include=set(ObservationPatchBody.model_fields.keys()), exclude_unset=True
        )

        for field, value in observation_data.items():
            setattr(observation, field, value)

        try:
            observation.save()
        except (
            IntegrityError,
            UniqueViolation,
        ):
            raise HttpError(409, "Duplicate phenomenonTime found on this datastream.")

        if (
            "phenomenon_time" in observation_data.keys()
            and update_datastream_statistics is True
        ):
            datastream_service.update_observation_statistics(
                datastream=datastream,
                fields=["phenomenon_begin_time", "phenomenon_end_time"],
            )

        return self.get(
            principal=principal,
            uid=observation.id,
            datastream_id=datastream_id,
            expand_related=expand_related,
        )

    def delete(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        datastream_id: Optional[uuid.UUID] = None,
        update_datastream_statistics: bool = True,
    ):
        datastream = datastream_service.get_datastream_for_action(
            principal, datastream_id, action="edit"
        )
        observation = self.get_observation_for_action(
            principal=principal,
            uid=uid,
            action="delete",
            datastream_id=datastream_id,
        )
        observation.delete()

        if update_datastream_statistics is True:
            datastream_service.update_observation_statistics(
                datastream=datastream,
                fields=["phenomenon_begin_time", "phenomenon_end_time", "value_count"],
            )

    def bulk_create(
        self,
        principal: User | APIKey,
        data: ObservationBulkPostBody,
        datastream_id: uuid.UUID,
        mode: Literal["insert", "append", "backfill", "replace"],
        update_datastream_statistics: bool = True,
    ):
        datastream = datastream_service.get_datastream_for_action(
            principal, datastream_id, action="edit"
        )
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=datastream.thing.workspace_id
        )

        if not Observation.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create these observations"
            )

        required_fields = {"phenomenonTime", "result"}
        if not required_fields.issubset(set(data.fields)):
            raise HttpError(400, "Missing required observation fields")

        field_map = {field: idx for idx, field in enumerate(data.fields)}
        idx_phenomenon = field_map["phenomenonTime"]
        idx_result = field_map["result"]

        no_data_value = datastream.no_data_value

        observations = [
            Observation(
                datastream_id=datastream_id,
                phenomenon_time=row[idx_phenomenon],
                result=(
                    no_data_value
                    if isinstance(row[idx_result], float)
                    and math.isnan(row[idx_result])
                    else row[idx_result]
                ),
            )
            for row in data.data
        ]

        if mode == "append" and datastream.phenomenon_end_time:
            if (
                min(obs.phenomenon_time for obs in observations)
                <= datastream.phenomenon_end_time
            ):
                raise HttpError(
                    400,
                    "All observations must occur after the datastream's end time for append mode",
                )

        elif mode == "backfill" and datastream.phenomenon_begin_time:
            if (
                max(obs.phenomenon_time for obs in observations)
                >= datastream.phenomenon_begin_time
            ):
                raise HttpError(
                    400,
                    "All observations must occur before the datastream's begin time for backfill mode",
                )

        elif mode == "replace":
            start_time = min(obs.phenomenon_time for obs in observations)
            end_time = max(obs.phenomenon_time for obs in observations)
            self.bulk_delete(
                principal=principal,
                data=ObservationBulkDeleteBody(
                    phenomenon_time_start=start_time,
                    phenomenon_time_end=end_time,
                ),
                datastream_id=datastream_id,
                update_datastream_statistics=False,
            )

        try:
            Observation.objects.bulk_copy(observations)
        except (
            IntegrityError,
            UniqueViolation,
        ):
            raise HttpError(409, "Duplicate phenomenonTime found on this datastream.")

        if update_datastream_statistics is True:
            datastream_service.update_observation_statistics(
                datastream=datastream,
                fields=["phenomenon_begin_time", "phenomenon_end_time", "value_count"],
            )

    def bulk_delete(
        self,
        principal: User | APIKey,
        data: ObservationBulkDeleteBody,
        datastream_id: uuid.UUID,
        update_datastream_statistics: bool = True,
    ):
        datastream = datastream_service.get_datastream_for_action(
            principal, datastream_id, action="edit"
        )

        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=datastream.thing.workspace_id
        )

        if not Observation.can_principal_delete(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to delete these observations"
            )

        queryset = Observation.objects.filter(datastream=datastream)

        if data.phenomenon_time_start is not None:
            queryset = queryset.filter(phenomenon_time__gte=data.phenomenon_time_start)
        if data.phenomenon_time_end is not None:
            queryset = queryset.filter(phenomenon_time__lte=data.phenomenon_time_end)

        queryset.delete()

        if update_datastream_statistics is True:
            datastream_service.update_observation_statistics(
                datastream=datastream,
                fields=["phenomenon_begin_time", "phenomenon_end_time", "value_count"],
            )

    def copy(
        self,
        principal: User | APIKey,
        response: HttpResponse,
        data: ObservationCopyBody,
        datastream_id: uuid.UUID,
    ):
        destination_datastream = datastream_service.get_datastream_for_action(
            principal, datastream_id, action="edit"
        )

        source_datastream = datastream_service.get_datastream_for_action(
            principal, data.source_datastream_id, action="view"
        )

        if (
            destination_datastream.thing.workspace_id
            != source_datastream.thing.workspace_id
        ):
            raise HttpError(
                400,
                "Source and destination datastreams must belong to the same workspace",
            )

        if (
            not data.phenomenon_time_start
            and not data.phenomenon_time_end
            and destination_datastream.value_count
        ) or (
            destination_datastream.phenomenon_begin_time
            and destination_datastream.phenomenon_end_time
            and (
                (
                    data.phenomenon_time_start
                    and data.phenomenon_time_start
                    <= destination_datastream.phenomenon_end_time
                )
                or (
                    data.phenomenon_time_end
                    and data.phenomenon_time_end
                    >= destination_datastream.phenomenon_begin_time
                )
            )
        ):
            raise HttpError(
                400,
                "Source and destination datastream phenomenon time ranges must not overlap",
            )

        return self.run_task(
            task_callable=copy_observations,
            response=response,
            source_datastream_id=str(source_datastream.id),
            destination_datastream_id=str(destination_datastream.id),
            phenomenon_time_start=data.phenomenon_time_start,
            phenomenon_time_end=data.phenomenon_time_end,
        )
