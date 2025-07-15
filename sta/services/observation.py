import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from pydantic.alias_generators import to_camel
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import Observation
from sta.schemas.observation import ObservationOrderByFields
from api.service import ServiceUtils

User = get_user_model()


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

    @staticmethod
    def get_observation_for_action(
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            observation = Observation.objects.select_related(
                "datastream", "datastream__thing", "datastream__thing__workspace"
            ).get(id=uid)
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

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        datastream_id: uuid.UUID,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
        response_format: Optional[str] = None,
    ):
        queryset = Observation.objects.filter(datastream_id=datastream_id)

        for field in [
            "phenomenon_time__lte",
            "phenomenon_time__gte",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(ObservationOrderByFields)),
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

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
            return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_observation_for_action(
            principal=principal, uid=uid, action="view"
        )
