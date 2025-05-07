import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import APIKey
from iam.services.utils import ServiceUtils
from sta.models import Sensor
from sta.schemas import SensorPostBody, SensorPatchBody
from sta.schemas.sensor import SensorFields

User = get_user_model()


class SensorService(ServiceUtils):
    @staticmethod
    def get_sensor_for_action(
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            sensor = Sensor.objects.select_related("workspace").get(pk=uid)
        except Sensor.DoesNotExist:
            raise HttpError(404, "Sensor does not exist")

        sensor_permissions = sensor.get_principal_permissions(principal=principal)

        if "view" not in sensor_permissions:
            raise HttpError(404, "Sensor does not exist")

        if action not in sensor_permissions:
            raise HttpError(403, f"You do not have permission to {action} this sensor")

        return sensor

    @staticmethod
    def list(
        principal: Optional[Union[User, APIKey]], workspace_id: Optional[uuid.UUID]
    ):
        queryset = Sensor.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(principal=principal).distinct()

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_sensor_for_action(principal=principal, uid=uid, action="view")

    def create(self, principal: Union[User, APIKey], data: SensorPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not Sensor.can_principal_create(principal=principal, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this sensor")

        sensor = Sensor.objects.create(
            workspace=workspace,
            **data.dict(include=set(SensorFields.model_fields.keys())),
        )

        return sensor

    def update(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: SensorPatchBody
    ):
        sensor = self.get_sensor_for_action(principal=principal, uid=uid, action="edit")
        sensor_data = data.dict(
            include=set(SensorFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in sensor_data.items():
            setattr(sensor, field, value)

        sensor.save()

        return sensor

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        sensor = self.get_sensor_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if sensor.datastreams.exists():
            raise HttpError(409, "Sensor in use by one or more datastreams")

        sensor.delete()

        return "Sensor deleted"
