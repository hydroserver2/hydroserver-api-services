import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import StreamingHttpResponse
from iam.services.utils import ServiceUtils
from sta.models import Datastream, Observation
from sta.schemas import DatastreamPostBody, DatastreamPatchBody
from sta.schemas.datastream import DatastreamFields
from sta.services import (
    ThingService,
    ObservedPropertyService,
    ProcessingLevelService,
    SensorService,
    UnitService,
)

User = get_user_model()

thing_service = ThingService()
observed_property_service = ObservedPropertyService()
processing_level_service = ProcessingLevelService()
sensor_service = SensorService()
unit_service = UnitService()


class DatastreamService(ServiceUtils):
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
    def get_datastream_for_action(
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        raise_400: bool = False,
    ):
        try:
            datastream = Datastream.objects.select_related(
                "thing", "thing__workspace"
            ).get(pk=uid)
        except Datastream.DoesNotExist:
            raise HttpError(404 if not raise_400 else 400, "Datastream does not exist")

        datastream_permissions = datastream.get_user_permissions(user=user)

        if "view" not in datastream_permissions:
            raise HttpError(404 if not raise_400 else 400, "Datastream does not exist")

        if action not in datastream_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this datastream",
            )

        return datastream

    @staticmethod
    def list(
        user: Optional[User],
        workspace_id: Optional[uuid.UUID],
        thing_id: Optional[uuid.UUID],
    ):
        queryset = Datastream.objects

        if workspace_id:
            queryset = queryset.filter(thing__workspace_id=workspace_id)

        if thing_id:
            queryset = queryset.filter(thing_id=thing_id)

        return queryset.visible(user=user).select_related("thing__workspace").distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_datastream_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: DatastreamPostBody):
        thing = self.handle_http_404_error(
            thing_service.get, user=user, uid=data.thing_id
        )

        if not Datastream.can_user_create(user=user, workspace=thing.workspace):
            raise HttpError(403, "You do not have permission to create this datastream")

        observed_property = self.handle_http_404_error(
            observed_property_service.get, user=user, uid=data.observed_property_id
        )
        if observed_property.workspace not in (
            thing.workspace,
            None,
        ):
            raise HttpError(
                400,
                "The given observed property cannot be associated with this datastream",
            )

        processing_level = self.handle_http_404_error(
            processing_level_service.get, user=user, uid=data.processing_level_id
        )
        if processing_level.workspace not in (
            thing.workspace,
            None,
        ):
            raise HttpError(
                400,
                "The given processing level cannot be associated with this datastream",
            )

        sensor = self.handle_http_404_error(
            sensor_service.get, user=user, uid=data.sensor_id
        )
        if sensor.workspace not in (
            thing.workspace,
            None,
        ):
            raise HttpError(
                400, "The given sensor cannot be associated with this datastream"
            )

        unit = self.handle_http_404_error(unit_service.get, user=user, uid=data.unit_id)
        if unit.workspace not in (
            thing.workspace,
            None,
        ):
            raise HttpError(
                400, "The given unit cannot be associated with this datastream"
            )

        datastream = Datastream.objects.create(
            **data.dict(include=set(DatastreamFields.model_fields.keys()))
        )

        return datastream

    def update(self, user: User, uid: uuid.UUID, data: DatastreamPatchBody):
        datastream = self.get_datastream_for_action(user=user, uid=uid, action="edit")
        datastream_data = data.dict(
            include=set(DatastreamFields.model_fields.keys()), exclude_unset=True
        )

        thing = (
            self.handle_http_404_error(thing_service.get, user=user, uid=data.thing_id)
            if data.thing_id
            else None
        )
        if thing and thing.workspace != datastream.thing.workspace:
            raise HttpError(
                400,
                "You cannot associate this datastream with a thing in another workspace",
            )

        observed_property = (
            self.handle_http_404_error(
                observed_property_service.get, user=user, uid=data.observed_property_id
            )
            if data.observed_property_id
            else None
        )
        if observed_property and observed_property.workspace not in (
            datastream.thing.workspace,
            None,
        ):
            raise HttpError(
                400,
                "The given observed property cannot be associated with this datastream",
            )

        processing_level = (
            self.handle_http_404_error(
                processing_level_service.get, user=user, uid=data.processing_level_id
            )
            if data.processing_level_id
            else None
        )
        if processing_level and processing_level.workspace not in (
            datastream.thing.workspace,
            None,
        ):
            raise HttpError(
                400,
                "The given processing level cannot be associated with this datastream",
            )

        sensor = (
            self.handle_http_404_error(
                sensor_service.get, user=user, uid=data.sensor_id
            )
            if data.sensor_id
            else None
        )
        if sensor and sensor.workspace not in (
            datastream.thing.workspace,
            None,
        ):
            raise HttpError(
                400, "The given sensor cannot be associated with this datastream"
            )

        unit = (
            self.handle_http_404_error(unit_service.get, user=user, uid=data.unit_id)
            if data.unit_id
            else None
        )
        if unit and unit.workspace not in (
            datastream.thing.workspace,
            None,
        ):
            raise HttpError(
                400, "The given unit cannot be associated with this datastream"
            )

        for field, value in datastream_data.items():
            setattr(datastream, field, value)

        datastream.save()

        return datastream

    def delete(self, user: User, uid: uuid.UUID):
        datastream = self.get_datastream_for_action(user=user, uid=uid, action="delete")
        datastream.delete()

        return "Datastream deleted"

    @staticmethod
    def generate_csv(datastream: Datastream):
        observations = (
            Observation.objects.filter(datastream=datastream)
            .only("phenomenon_time", "result", "quality_code")
            .order_by("phenomenon_time")
        )

        latitude = (
            round(datastream.thing.location.latitude, 6)
            if datastream.thing.location.latitude
            else "None"
        )
        longitude = (
            round(datastream.thing.location.longitude, 6)
            if datastream.thing.location.longitude
            else "None"
        )
        elevation_m = (
            round(datastream.thing.location.elevation_m, 6)
            if datastream.thing.location.elevation_m
            else "None"
        )

        yield (
            f"# =============================================================================\n"
            f"# Generated on: {timezone.now().isoformat()}\n"
            f"# \n"
            f"# Workspace:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.thing.workspace.name}\n"
            f"# Owner: {datastream.thing.workspace.owner.name()}\n"
            f"# Contact Email: {datastream.thing.workspace.owner.email}\n"
            f"#\n"
            f"# Site Information:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.thing.name}\n"
            f"# Description: {datastream.thing.description}\n"
            f"# SamplingFeatureType: {datastream.thing.sampling_feature_type}\n"
            f"# SamplingFeatureCode: {datastream.thing.sampling_feature_code}\n"
            f"# SiteType: {datastream.thing.site_type}\n"
            f"#\n"
            f"# Location Information:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.thing.location.name}\n"
            f"# Description: {datastream.thing.location.description}\n"
            f"# Latitude: {latitude}\n"
            f"# Longitude: {longitude}\n"
            f"# Elevation_m: {elevation_m}\n"
            f"# ElevationDatum: {datastream.thing.location.elevation_datum}\n"
            f"# State: {datastream.thing.location.state}\n"
            f"# County: {datastream.thing.location.county}\n"
            f"#\n"
            f"# Datastream Information:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.name}\n"
            f"# Description: {datastream.description}\n"
            f"# ObservationType: {datastream.observation_type}\n"
            f"# ResultType: {datastream.result_type}\n"
            f"# Status: {datastream.status}\n"
            f"# SampledMedium: {datastream.sampled_medium}\n"
            f"# ValueCount: {datastream.value_count}\n"
            f"# NoDataValue: {datastream.no_data_value}\n"
            f"# IntendedTimeSpacing: {datastream.intended_time_spacing}\n"
            f"# IntendedTimeSpacingUnit: {datastream.intended_time_spacing_unit}\n"
            f"# AggregationStatistic: {datastream.aggregation_statistic}\n"
            f"# TimeAggregationInterval: {datastream.time_aggregation_interval}\n"
            f"# TimeAggregationIntervalUnit: {datastream.time_aggregation_interval_unit}\n"
            f"#\n"
            f"# Method Information:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.sensor.name}\n"
            f"# Description: {datastream.sensor.description}\n"
            f"# MethodCode: {datastream.sensor.method_code}\n"
            f"# MethodType: {datastream.sensor.method_type}\n"
            f"# MethodLink: {datastream.sensor.method_link}\n"
            f"# SensorManufacturerName: {datastream.sensor.manufacturer}\n"
            f"# SensorModelName: {datastream.sensor.sensor_model}\n"
            f"# SensorModelLink: {datastream.sensor.sensor_model_link}\n"
            f"#\n"
            f"# Observed Property Information:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.observed_property.name}\n"
            f"# Definition: {datastream.observed_property.definition}\n"
            f"# Description: {datastream.observed_property.description}\n"
            f"# VariableType: {datastream.observed_property.observed_property_type}\n"
            f"# VariableCode: {datastream.observed_property.code}\n"
            f"#\n"
            f"# Unit Information:\n"
            f"# -------------------------------------\n"
            f"# Name: {datastream.unit.name}\n"
            f"# Symbol: {datastream.unit.symbol}\n"
            f"# Definition: {datastream.unit.definition}\n"
            f"# UnitType: {datastream.unit.unit_type}\n"
            f"#\n"
            f"# Processing Level Information:\n"
            f"# -------------------------------------\n"
            f"# Code: {datastream.processing_level.code}\n"
            f"# Definition: {datastream.processing_level.definition}\n"
            f"# Explanation: {datastream.processing_level.explanation}\n"
            f"#\n"
            f"# Data Disclaimer:\n"
            f"# -------------------------------------\n"
            f"# Output date/time values are in UTC unless they were input to HydroServer without time zone offset information. In that case, date/time values are output as they were supplied to HydroServer.\n"
            f"# {datastream.thing.data_disclaimer if datastream.thing.data_disclaimer else ''}\n"
            f"# =============================================================================\n"
        )

        yield "ResultTime,Result,ResultQualifiers\n"

        for observation in observations.all():
            if observation.quality_code:
                yield f'{observation.phenomenon_time.isoformat()},{observation.result},"{observation.quality_code}"\n'
            else:
                yield f"{observation.phenomenon_time.isoformat()},{observation.result},\n"

    def get_csv(self, user: User, uid: uuid.UUID):
        datastream = self.get_datastream_for_action(user=user, uid=uid, action="view")

        response = StreamingHttpResponse(
            self.generate_csv(datastream), content_type="text/csv"
        )
        response["Content-Disposition"] = f'attachment; filename="{datastream.name}.csv"'

        return response
