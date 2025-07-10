import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import Sensor, SensorEncodingType, MethodType
from sta.schemas import SensorPostBody, SensorPatchBody
from sta.schemas.sensor import SensorFields, SensorOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class SensorService(ServiceUtils):
    @staticmethod
    def get_sensor_for_action(
        principal: User | APIKey,
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

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = Sensor.objects

        for field in [
            "workspace_id",
            "datastreams__thing_id",
            "datastreams__id",
            "encoding_type",
            "manufacturer",
            "method_type",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(SensorOrderByFields)),
                {
                    "model": "sensor_model"
                }
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_sensor_for_action(principal=principal, uid=uid, action="view")

    def create(self, principal: User | APIKey, data: SensorPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        ) if data.workspace_id else (None, None,)

        if not Sensor.can_principal_create(principal=principal, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this sensor")

        sensor = Sensor.objects.create(
            workspace=workspace,
            **data.dict(include=set(SensorFields.model_fields.keys())),
        )

        return sensor

    def update(
        self, principal: User | APIKey, uid: uuid.UUID, data: SensorPatchBody
    ):
        sensor = self.get_sensor_for_action(principal=principal, uid=uid, action="edit")
        sensor_data = data.dict(
            include=set(SensorFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in sensor_data.items():
            setattr(sensor, field, value)

        sensor.save()

        return sensor

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        sensor = self.get_sensor_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if sensor.datastreams.exists():
            raise HttpError(409, "Sensor in use by one or more datastreams")

        sensor.delete()

        return "Sensor deleted"

    def list_method_types(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False
    ):
        queryset = MethodType.objects.order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list(
            "name", flat=True
        )

    def list_encoding_types(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False
    ):
        queryset = SensorEncodingType.objects.order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list(
            "name", flat=True
        )
