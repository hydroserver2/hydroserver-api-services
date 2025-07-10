import uuid
from datetime import datetime
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import Observation
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





















    @staticmethod
    def list(
        principal: Optional[User | APIKey],
        workspace_id: Optional[uuid.UUID],
        thing_id: Optional[uuid.UUID],
        datastream_id: Optional[uuid.UUID],
    ):
        queryset = Observation.objects

        if workspace_id:
            queryset = queryset.filter(datastream__thing__workspace_id=workspace_id)

        if thing_id:
            queryset = queryset.filter(datastream__thing_id=thing_id)

        if datastream_id:
            queryset = queryset.filter(datastream_id=datastream_id)

        return queryset.visible(principal=principal).distinct()

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_observation_for_action(
            principal=principal, uid=uid, action="view"
        )




    def list(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        phenomenon_start_time: Optional[datetime] = None,
        phenomenon_end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: Optional[int] = None,
        order: Literal["asc", "desc"] = "desc",
    ):
        datastream = self.get_datastream_for_action(
            principal=principal, uid=uid, action="view"
        )

        fields = ["phenomenon_time", "result"]

        queryset = Observation.objects.filter(datastream=datastream)
        order_by = "phenomenon_time" if order == "asc" else "-phenomenon_time"

        if phenomenon_start_time:
            queryset = queryset.filter(phenomenon_time__gte=phenomenon_start_time)
        if phenomenon_end_time:
            queryset = queryset.filter(phenomenon_time__lte=phenomenon_end_time)

        queryset = queryset.order_by(order_by)

        if page_size is not None:
            page = max(1, page)
            page_size = max(0, page_size)
            start = (page - 1) * page_size
            end = start + page_size

            queryset = queryset[start:end]

        observations = list(queryset.values_list(*fields))

        if observations:
            response = dict(zip(fields, zip(*observations)))
        else:
            response = {field: [] for field in fields}

        return response


