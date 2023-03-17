from ninja import Schema, Field
from pydantic import HttpUrl
from typing import List, Literal, Union
from hydrothings import components as st_components
from hydrothings.extras.iso_types import ISOInterval


class DatastreamProperties(Schema):
    result_type: str = Field(..., alias='resultType')
    status: Union[str, None] = None
    sampled_medium: str = Field(..., alias='sampledMedium')
    value_count: Union[int, None] = Field(None, alias='valueCount')
    no_data_value: float = Field(..., alias='noDataValue')
    processing_level_code: str = Field(..., alias='processingLevelCode')
    intended_time_spacing: Union[float, None] = Field(None, alias='intendedTimeSpacing')
    intended_time_spacing_units: Union[st_components.UnitOfMeasurement, None] = Field(
        None, alias='intendedTimeSpacingUnitOfMeasurement'
    )
    aggregation_statistic: Union[str, None] = Field(None, alias='aggregationStatistic')
    time_aggregation_interval: float = Field(None, alias='timeAggregationInterval')
    time_aggregation_interval_units: Union[st_components.UnitOfMeasurement, None] = Field(
        None, alias='timeAggregationIntervalUnitOfMeasurement'
    )
    phenomenon_time: Union[ISOInterval, None] = Field(None, alias='phenomenonTime')
    result_time: Union[ISOInterval, None] = Field(None, alias='resultTime')

    class Config:
        allow_population_by_field_name = True


class Datastream(Schema):
    properties: DatastreamProperties


class LocationProperties(Schema):
    city: Union[str, None] = None
    state: Union[str, None] = None
    county: Union[str, None] = None
    elevation_m: Union[float, None] = None
    elevation_datum: Union[str, None] = Field(None, alias='elevationDatum')

    class Config:
        allow_population_by_field_name = True


class Location(Schema):
    properties: LocationProperties


class ObservedPropertyProperties(Schema):
    variable_code: str = Field(..., alias='variableCode')
    variable_type: str = Field(..., alias='variableType')

    class Config:
        allow_population_by_field_name = True


class ObservedProperty(Schema):
    properties: ObservedPropertyProperties


class SensorModel(Schema):
    sensor_model_name: str = Field(..., alias='sensorModelName')
    sensor_model_url: Union[HttpUrl, None] = Field(None, alias='sensorModelURL')
    sensor_manufacturer: str = Field(..., alias='sensorManufacturer')

    class Config:
        allow_population_by_field_name = True


sensorEncodingTypes = Literal[
    'application/pdf',
    'http://www.opengis.net/doc/IS/SensorML/2.0',
    'text/html',
    'application/json'
]


class SensorProperties(Schema):
    method_code: Union[str, None] = Field(None, alias='methodCode')
    method_type: str = Field(..., alias='methodType')
    method_link: Union[HttpUrl, None] = Field(None, alias='methodLink')
    sensor_model: SensorModel = Field(..., alias='sensorModel')

    class Config:
        allow_population_by_field_name = True


class Sensor(Schema):
    encoding_type: sensorEncodingTypes = Field(..., alias='encodingType')
    sensor_metadata: SensorProperties = Field(..., alias='metadata')


class ContactPerson(Schema):
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str = Field(..., alias='email')

    class Config:
        allow_population_by_field_name = True


class ThingProperties(Schema):
    sampling_feature_type: str = Field(..., alias='samplingFeatureType')
    sampling_feature_code: str = Field(..., alias='samplingFeatureCode')
    site_type: str = Field(..., alias='siteType')
    contact_people: List[ContactPerson] = Field(..., alias='contactPeople')

    class Config:
        allow_population_by_field_name = True


class Thing(Schema):
    properties: ThingProperties
