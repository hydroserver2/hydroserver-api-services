from ninja import Schema, Field
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from typing import Literal, Optional
from sensorthings.types import AnyHttpUrlString
from sensorthings.components.sensors.schemas import (SensorGetResponse as DefaultSensorGetResponse,
                                                     SensorListResponse as DefaultSensorListResponse)


class SensorModel(Schema):
    sensor_model_name: Optional[str] = None
    sensor_model_url: Optional[AnyHttpUrlString] = None
    sensor_manufacturer: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel)


sensorEncodingTypes = Literal[
    "application/pdf",
    "http://www.opengis.net/doc/IS/SensorML/2.0",
    "text/html",
    "application/json"
]


class SensorProperties(Schema):
    method_code: Optional[str] = None
    method_type: str
    method_link: Optional[AnyHttpUrlString] = None
    sensor_model: SensorModel

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel)


class SensorGetResponse(DefaultSensorGetResponse):
    encoding_type: sensorEncodingTypes
    sensor_metadata: SensorProperties = Field(..., alias="metadata")

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel)


class SensorListResponse(DefaultSensorListResponse):
    value: list[SensorGetResponse]
