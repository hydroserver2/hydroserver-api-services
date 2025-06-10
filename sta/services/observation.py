import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import Observation
from hydroserver.service import ServiceUtils

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
        principal: Union[User, APIKey],
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
        principal: Optional[Union[User, APIKey]],
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

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_observation_for_action(
            principal=principal, uid=uid, action="view"
        )
