import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import StreamingHttpResponse
from api.service import ServiceUtils
from iam.models import APIKey
from sta.models import Datastream, Observation, DatastreamAggregation, DatastreamStatus, SampledMedium
from sta.schemas import DatastreamPostBody, DatastreamPatchBody
from sta.schemas.datastream import DatastreamOrderByFields
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
        principal: User | APIKey,
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

        datastream_permissions = datastream.get_principal_permissions(
            principal=principal
        )

        if "view" not in datastream_permissions:
            raise HttpError(404 if not raise_400 else 400, "Datastream does not exist")

        if action not in datastream_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this datastream",
            )

        return datastream

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = Datastream.objects

        for field in [
            "thing__workspace_id",
            "thing_id",
            "sensor_id",
            "observed_property_id",
            "processing_level_id",
            "unit_id",
            "observation_type",
            "sampled_medium",
            "status",
            "result_type",
            "is_private",
            "value_count__lte",
            "value_count__gte",
            "phenomenon_begin_time__lte",
            "phenomenon_begin_time__gte",
            "phenomenon_end_time__lte",
            "phenomenon_end_time__gte",
            "result_begin_time__lte",
            "result_begin_time__gte",
            "result_end_time__lte",
            "result_end_time__gte",
        ]:
            if field in filtering:
                if field == "is_private":
                    queryset = self.apply_filters(
                        queryset, f"is_private", filtering[field]
                    )
                    queryset = self.apply_filters(
                        queryset, f"thing__is_private", filtering[field]
                    )
                    queryset = self.apply_filters(
                        queryset, f"thing__workspace__is_private", filtering[field]
                    )
                else:
                    queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(DatastreamOrderByFields)),
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_datastream_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: User | APIKey, data: DatastreamPostBody):
        thing = self.handle_http_404_error(
            thing_service.get, principal=principal, uid=data.thing_id
        )

        if not Datastream.can_principal_create(
            principal=principal, workspace=thing.workspace
        ):
            raise HttpError(403, "You do not have permission to create this datastream")

        observed_property = self.handle_http_404_error(
            observed_property_service.get,
            principal=principal,
            uid=data.observed_property_id,
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
            processing_level_service.get,
            principal=principal,
            uid=data.processing_level_id,
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
            sensor_service.get, principal=principal, uid=data.sensor_id
        )
        if sensor.workspace not in (
            thing.workspace,
            None,
        ):
            raise HttpError(
                400, "The given sensor cannot be associated with this datastream"
            )

        unit = self.handle_http_404_error(
            unit_service.get, principal=principal, uid=data.unit_id
        )
        if unit.workspace not in (
            thing.workspace,
            None,
        ):
            raise HttpError(
                400, "The given unit cannot be associated with this datastream"
            )

        datastream = Datastream.objects.create(
            **data.dict(include=set(DatastreamPostBody.model_fields.keys()))
        )

        return datastream

    def update(
        self, principal: User | APIKey, uid: uuid.UUID, data: DatastreamPatchBody
    ):
        datastream = self.get_datastream_for_action(
            principal=principal, uid=uid, action="edit"
        )
        datastream_data = data.dict(
            include=set(DatastreamPatchBody.model_fields.keys()), exclude_unset=True
        )

        thing = (
            self.handle_http_404_error(
                thing_service.get, principal=principal, uid=data.thing_id
            )
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
                observed_property_service.get,
                principal=principal,
                uid=data.observed_property_id,
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
                processing_level_service.get,
                principal=principal,
                uid=data.processing_level_id,
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
                sensor_service.get, principal=principal, uid=data.sensor_id
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
            self.handle_http_404_error(
                unit_service.get, principal=principal, uid=data.unit_id
            )
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

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        datastream = self.get_datastream_for_action(
            principal=principal, uid=uid, action="delete"
        )
        datastream.delete()

        return "Datastream deleted"

    def list_aggregation_statistics(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False
    ):
        queryset = DatastreamAggregation.objects.filter(public=True).order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list(
            "name", flat=True
        )

    def list_statuses(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False
    ):
        queryset = DatastreamStatus.objects.filter(public=True).order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list(
            "name", flat=True
        )

    def list_sampled_mediums(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False
    ):
        queryset = SampledMedium.objects.filter(public=True).order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list(
            "name", flat=True
        )

    @staticmethod
    def generate_csv(datastream: Datastream):
        observations = Observation.objects.filter(datastream=datastream).order_by(
            "phenomenon_time"
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

        for observation in observations.values_list(
            "phenomenon_time", "result", "quality_code"
        ):
            if observation[2]:
                yield f'{observation[0].isoformat()},{observation[1]},"{observation[2]}"\n'
            else:
                yield f"{observation[0].isoformat()},{observation[1]},\n"

    def get_csv(self, principal: User | APIKey, uid: uuid.UUID):
        datastream = self.get_datastream_for_action(
            principal=principal, uid=uid, action="view"
        )

        response = StreamingHttpResponse(
            self.generate_csv(datastream), content_type="text/csv"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{datastream.name}.csv"'
        )

        return response
