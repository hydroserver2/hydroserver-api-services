from uuid import UUID
from ninja import Schema, Field
from typing import List, Literal, Union, Optional
from datetime import datetime
from sensorthings import components as st_components
from sensorthings.types import AnyHttpUrlString


class DatastreamProperties(Schema):
    result_type: str = Field(..., alias='resultType')
    status: Union[str, None] = None
    sampled_medium: str = Field(..., alias='sampledMedium')
    value_count: Union[int, None] = Field(None, alias='valueCount')
    no_data_value: float = Field(..., alias='noDataValue')
    processing_level_code: str = Field(..., alias='processingLevelCode')
    intended_time_spacing: Union[float, None] = Field(None, alias='intendedTimeSpacing')
    intended_time_spacing_units: Union[str, None] = Field(None, alias='intendedTimeSpacingUnitOfMeasurement')
    aggregation_statistic: Union[str, None] = Field(None, alias='aggregationStatistic')
    time_aggregation_interval: float = Field(None, alias='timeAggregationInterval')
    time_aggregation_interval_units: Union[st_components.UnitOfMeasurement, None] = Field(
        None, alias='timeAggregationIntervalUnitOfMeasurement'
    )
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class DatastreamGetResponse(st_components.DatastreamGetResponse):
    observation_type: Optional[str] = Field(None, alias='observationType')
    properties: Optional[DatastreamProperties] = None

    class Config:
        populate_by_name = True


class DatastreamListResponse(st_components.DatastreamListResponse):
    value: List[DatastreamGetResponse]


class LocationProperties(Schema):
    state: Union[str, None] = None
    county: Union[str, None] = None
    elevation_m: Union[float, None] = None
    elevation_datum: Union[str, None] = Field(None, alias='elevationDatum')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class LocationGetResponse(st_components.LocationGetResponse):
    properties: Optional[LocationProperties] = None


class LocationListResponse(st_components.LocationListResponse):
    value: List[LocationGetResponse]


class ObservedPropertyProperties(Schema):
    variable_code: str = Field(..., alias='variableCode')
    variable_type: str = Field(..., alias='variableType')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class ObservedPropertyGetResponse(st_components.ObservedPropertyGetResponse):
    definition: Optional[str] = None
    properties: Optional[ObservedPropertyProperties] = None


class ObservedPropertyListResponse(st_components.ObservedPropertyListResponse):
    value: List[ObservedPropertyGetResponse]


class SensorModel(Schema):
    sensor_model_name: str = Field(..., alias='sensorModelName')
    sensor_model_url: Union[AnyHttpUrlString, None] = Field(None, alias='sensorModelURL')
    sensor_manufacturer: str = Field(..., alias='sensorManufacturer')

    class Config:
        populate_by_name = True


sensorEncodingTypes = Literal[
    'application/pdf',
    'http://www.opengis.net/doc/IS/SensorML/2.0',
    'text/html',
    'application/json'
]


class SensorProperties(Schema):
    method_code: Union[str, None] = Field(None, alias='methodCode')
    method_type: str = Field(..., alias='methodType')
    method_link: Union[AnyHttpUrlString, None] = Field(None, alias='methodLink')
    sensor_model: SensorModel = Field(..., alias='sensorModel')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class SensorGetResponse(st_components.SensorGetResponse):
    encoding_type: Optional[sensorEncodingTypes] = Field(None, alias='encodingType')
    sensor_metadata: Optional[SensorProperties] = Field(None, alias='metadata')

    class Config:
        populate_by_name = True


class SensorListResponse(st_components.SensorListResponse):
    value: List[SensorGetResponse]


class ContactPerson(Schema):
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str = Field(..., alias='email')
    organization_name: Optional[str] = Field(None, alias='organizationName')

    class Config:
        populate_by_name = True


class ThingProperties(Schema):
    sampling_feature_type: str = Field(..., alias='samplingFeatureType')
    sampling_feature_code: str = Field(..., alias='samplingFeatureCode')
    site_type: str = Field(..., alias='siteType')
    contact_people: List[ContactPerson] = Field(..., alias='contactPeople')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class ThingGetResponse(st_components.ThingGetResponse):
    properties: Optional[ThingProperties] = None


class ThingListResponse(st_components.ThingListResponse):
    value: List[ThingGetResponse]


class ResultQualifier(Schema):
    code: str
    description: str


class ResultQualityResponse(Schema):
    quality_code: Optional[str] = Field(None, alias='qualityCode')
    result_qualifiers: Optional[List[ResultQualifier]] = Field(None, alias='resultQualifiers')

    class Config:
        populate_by_name = True


class ResultQualityBody(Schema):
    quality_code: Optional[str] = Field(None, alias='qualityCode')
    result_qualifiers: Optional[List[UUID]] = Field(None, alias='resultQualifiers')

    class Config:
        populate_by_name = True


class ObservationGetResponse(st_components.ObservationGetResponse):
    result_quality: Optional[ResultQualityResponse] = Field(None, alias='resultQuality')

    class Config:
        populate_by_name = True


class ObservationListResponse(st_components.ObservationListResponse):
    value: List[ObservationGetResponse]


class ObservationPostBody(st_components.ObservationPostBody):
    result_quality: Optional[ResultQualityBody] = Field(None, alias='resultQuality')

    class Config:
        populate_by_name = True


class ObservationPatchBody(st_components.ObservationPatchBody):
    result_quality: Optional[ResultQualityBody] = Field(None, alias='resultQuality')

    class Config:
        populate_by_name = True
