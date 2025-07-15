import uuid
from typing import Literal, Optional, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from iam.models import APIKey
from sta.services.datastream import DatastreamService
from etl.models import DataSource
from etl.schemas import DataSourcePostBody, DataSourcePatchBody
from etl.schemas.data_source import (
    DataSourceFields,
    DataSourceSummaryResponse,
    DataSourceDetailResponse,
)
from etl.schemas.orchestration_configuration import (
    OrchestrationConfigurationOrderByFields,
)
from api.service import ServiceUtils

from etl.schemas.orchestration_configuration import (
    OrchestrationConfigurationScheduleFields,
    OrchestrationConfigurationStatusFields,
)

from .orchestration_configuration import OrchestrationConfigurationUtils

User = get_user_model()

datastream_service = DatastreamService()


class DataSourceService(ServiceUtils, OrchestrationConfigurationUtils):

    def get_data_source_for_action(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        expand_related: bool = False,
        raise_400: bool = False,
    ):
        try:
            data_source = DataSource.objects
            if expand_related:
                data_source = self.select_expanded_fields(data_source)
            data_source = data_source.get(pk=uid)
        except DataSource.DoesNotExist:
            raise HttpError(404 if not raise_400 else 400, "Data source does not exist")

        data_source_permissions = data_source.get_principal_permissions(
            principal=principal
        )

        if "view" not in data_source_permissions:
            raise HttpError(404 if not raise_400 else 400, "Data source does not exist")

        if action not in data_source_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this data source",
            )

        return data_source

    @staticmethod
    def select_expanded_fields(queryset: QuerySet) -> QuerySet:
        return queryset.select_related(
            "workspace", "orchestration_system"
        ).prefetch_related("datastreams")

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
        expand_related: bool = False,
    ):
        queryset = DataSource.objects

        for field in [
            "workspace_id",
            "orchestration_system_id",
            "datastreams__id",
            "last_run_successful",
            "last_run__lte",
            "last_run__gte",
            "next_run__lte",
            "next_run__gte",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(OrchestrationConfigurationOrderByFields)),
            )

        if expand_related:
            queryset = self.select_expanded_fields(queryset)

        queryset = queryset.visible(principal=principal).distinct()
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return [
            (
                DataSourceDetailResponse.model_validate(data_source)
                if expand_related
                else DataSourceSummaryResponse.model_validate(data_source)
            )
            for data_source in queryset.all()
        ]

    def get(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        expand_related: bool = False,
    ):
        data_source = self.get_data_source_for_action(
            principal=principal, uid=uid, action="view", expand_related=expand_related
        )

        return (
            DataSourceDetailResponse.model_validate(data_source)
            if expand_related
            else DataSourceSummaryResponse.model_validate(data_source)
        )

    def create(
        self,
        principal: User | APIKey,
        data: DataSourcePostBody,
        expand_related: bool = False,
    ):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not DataSource.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this data source"
            )

        orchestration_system = self.validate_orchestration_system(
            principal=principal,
            orchestration_system_id=data.orchestration_system_id,
            workspace=workspace,
        )

        if data.schedule is not None:
            self.validate_scheduling(
                crontab=data.schedule.crontab,
                interval=data.schedule.interval,
                interval_units=data.schedule.interval_units,
            )

        data_source = DataSource.objects.create(
            workspace=workspace,
            orchestration_system=orchestration_system,
            **data.dict(include=set(DataSourceFields.model_fields.keys())),
            **(
                data.schedule.dict(
                    include=set(
                        OrchestrationConfigurationScheduleFields.model_fields.keys()
                    )
                )
                if data.schedule
                else {}
            ),
            **(
                data.status.dict(
                    include=set(
                        OrchestrationConfigurationStatusFields.model_fields.keys()
                    )
                )
                if data.status
                else {}
            ),
        )

        if data.datastream_ids:
            for datastream_id in data.datastream_ids:
                self.link_datastream(
                    principal=principal, uid=data_source.id, datastream_id=datastream_id
                )

        data_source = self.get_data_source_for_action(
            principal=principal,
            uid=data_source.id,
            action="view",
            expand_related=expand_related,
        )

        return (
            DataSourceDetailResponse.model_validate(data_source)
            if expand_related
            else DataSourceSummaryResponse.model_validate(data_source)
        )

    def update(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        data: DataSourcePatchBody,
        expand_related: bool = False,
    ):
        data_source = self.get_data_source_for_action(
            principal=principal, uid=uid, action="edit", expand_related=expand_related
        )
        data_source_data = data.dict(
            include=set(DataSourceFields.model_fields.keys()),
            exclude_unset=True,
        )

        if data.orchestration_system_id:
            orchestration_system = self.validate_orchestration_system(
                principal=principal,
                orchestration_system_id=data.orchestration_system_id,
                workspace=data_source.workspace,
            )
            data_source_data["orchestration_system_id"] = orchestration_system.id

        if "schedule" in data.model_fields_set:
            if data.schedule is not None:
                self.validate_scheduling(
                    crontab=data.schedule.crontab,
                    interval=data.schedule.interval,
                    interval_units=data.schedule.interval_units,
                )
                data_source_data.update(
                    data.schedule.dict(
                        include=set(
                            OrchestrationConfigurationScheduleFields.model_fields.keys()
                        ),
                        exclude_unset=True,
                    )
                )
            else:
                data_source_data.update(
                    {
                        key: field.default
                        for key, field in OrchestrationConfigurationScheduleFields.model_fields.items()
                    }
                )

        if "status" in data.model_fields_set:
            if data.status is not None:
                data_source_data.update(
                    data.status.dict(
                        include=set(
                            OrchestrationConfigurationStatusFields.model_fields.keys()
                        ),
                        exclude_unset=True,
                    )
                )
            else:
                data_source_data.update(
                    {
                        key: False if key == "paused" else field.default
                        for key, field in OrchestrationConfigurationStatusFields.model_fields.items()
                    }
                )

        for field, value in data_source_data.items():
            setattr(data_source, field, value)

        data_source.save()

        return (
            DataSourceDetailResponse.model_validate(data_source)
            if expand_related
            else DataSourceSummaryResponse.model_validate(data_source)
        )

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        data_source = self.get_data_source_for_action(
            principal=principal, uid=uid, action="delete"
        )

        data_source.delete()

        return "Data source deleted"

    def link_datastream(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        datastream_id: uuid.UUID,
    ):
        data_source = self.get_data_source_for_action(
            principal=principal, uid=uid, action="edit"
        )
        datastream = datastream_service.get_datastream_for_action(
            principal=principal, uid=datastream_id, action="edit"
        )

        if datastream.data_source is not None:
            raise HttpError(400, "Datastream has already been linked to a data source")

        if data_source.workspace != datastream.thing.workspace:
            raise HttpError(
                400, "The datastream must share a workspace with the data source"
            )

        datastream.data_source = data_source
        datastream.save()

        return "Data source configured for datastream"

    def unlink_datastream(
        self, principal: User | APIKey, uid: uuid.UUID, datastream_id: uuid.UUID
    ):
        data_source = self.get_data_source_for_action(
            principal=principal, uid=uid, action="edit"
        )
        datastream = datastream_service.get_datastream_for_action(
            principal=principal, uid=datastream_id, action="edit"
        )

        if datastream.data_source != data_source:
            raise HttpError(
                400, "The given data source is not configured for this datastream"
            )

        datastream.data_source = None
        datastream.save()

        return "Datastream unlinked from data source"
