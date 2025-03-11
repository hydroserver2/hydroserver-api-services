import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.models import Datastream
from sta.schemas import DatastreamPostBody, DatastreamPatchBody
from sta.schemas.datastream import DatastreamFields
from sta.services import ThingService, ObservedPropertyService, ProcessingLevelService, SensorService, UnitService

User = get_user_model()

thing_service = ThingService()
observed_property_service = ObservedPropertyService()
processing_level_service = ProcessingLevelService()
sensor_service = SensorService()
unit_service = UnitService()


class DatastreamService(ServiceUtils):
    @staticmethod
    def get_datastream_for_action(user: User, uid: uuid.UUID, action: Literal["view", "edit", "delete"],
                                  raise_400: bool = False):
        try:
            datastream = Datastream.objects.select_related("thing", "thing__workspace").get(pk=uid)
        except Datastream.DoesNotExist:
            raise HttpError(404 if not raise_400 else 400, "Datastream does not exist")

        datastream_permissions = datastream.get_user_permissions(user=user)

        if "view" not in datastream_permissions:
            raise HttpError(404 if not raise_400 else 400, "Datastream does not exist")

        if action not in datastream_permissions:
            raise HttpError(403 if not raise_400 else 400, f"You do not have permission to {action} this datastream")

        return datastream

    @staticmethod
    def list(user: Optional[User], workspace_id: Optional[uuid.UUID], thing_id: Optional[uuid.UUID]):
        queryset = Datastream.objects

        if workspace_id:
            queryset = queryset.filter(thing__workspace_id=workspace_id)

        if thing_id:
            queryset = queryset.filter(thing_id=thing_id)

        return queryset.visible(user=user).distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_datastream_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: DatastreamPostBody):
        thing = self.handle_http_404_error(thing_service.get, user=user, uid=data.thing_id)

        if not Datastream.can_user_create(user=user, workspace=thing.workspace):
            raise HttpError(403, "You do not have permission to create this datastream")

        observed_property = self.handle_http_404_error(observed_property_service.get, user=user,
                                                       uid=data.observed_property_id)
        if observed_property.workspace not in (thing.workspace, None,):
            raise HttpError(400, "The given observed property cannot be associated with this datastream")

        processing_level = self.handle_http_404_error(processing_level_service.get, user=user,
                                                      uid=data.processing_level_id)
        if processing_level.workspace not in (thing.workspace, None,):
            raise HttpError(400, "The given processing level cannot be associated with this datastream")

        sensor = self.handle_http_404_error(sensor_service.get, user=user, uid=data.sensor_id)
        if sensor.workspace not in (thing.workspace, None,):
            raise HttpError(400, "The given sensor cannot be associated with this datastream")

        unit = self.handle_http_404_error(unit_service.get, user=user, uid=data.unit_id)
        if unit.workspace not in (thing.workspace, None,):
            raise HttpError(400, "The given unit cannot be associated with this datastream")

        datastream = Datastream.objects.create(
            **data.dict(include=set(DatastreamFields.model_fields.keys()))
        )

        return datastream

    def update(self, user: User, uid: uuid.UUID, data: DatastreamPatchBody):
        datastream = self.get_datastream_for_action(user=user, uid=uid, action="edit")
        datastream_data = data.dict(include=set(DatastreamFields.model_fields.keys()), exclude_unset=True)

        thing = self.handle_http_404_error(
            thing_service.get, user=user, uid=data.thing_id
        ) if data.thing_id else None
        if thing and thing.workspace != datastream.thing.workspace:
            raise HttpError(400, "You cannot associate this datastream with a thing in another workspace")

        observed_property = self.handle_http_404_error(
            observed_property_service.get, user=user, uid=data.observed_property_id
        ) if data.observed_property_id else None
        if observed_property and observed_property.workspace not in (datastream.thing.workspace, None,):
            raise HttpError(400, "The given observed property cannot be associated with this datastream")

        processing_level = self.handle_http_404_error(
            processing_level_service.get, user=user, uid=data.processing_level_id
        ) if data.processing_level_id else None
        if processing_level and processing_level.workspace not in (datastream.thing.workspace, None,):
            raise HttpError(400, "The given processing level cannot be associated with this datastream")

        sensor = self.handle_http_404_error(
            sensor_service.get, user=user, uid=data.sensor_id
        ) if data.sensor_id else None
        if sensor and sensor.workspace not in (datastream.thing.workspace, None,):
            raise HttpError(400, "The given sensor cannot be associated with this datastream")

        unit = self.handle_http_404_error(
            unit_service.get, user=user, uid=data.unit_id
        ) if data.unit_id else None
        if unit and unit.workspace not in (datastream.thing.workspace, None,):
            raise HttpError(400, "The given unit cannot be associated with this datastream")

        for field, value in datastream_data.items():
            setattr(datastream, field, value)

        datastream.save()

        return datastream

    def delete(self, user: User, uid: uuid.UUID):
        datastream = self.get_datastream_for_action(user=user, uid=uid, action="delete")
        datastream.delete()

        return "Datastream deleted"
