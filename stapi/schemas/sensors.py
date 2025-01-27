from ninja import Schema, Field
from pydantic import ConfigDict
from typing import List, Literal, Union, Optional
from datetime import datetime
from sensorthings.types import AnyHttpUrlString
from sensorthings.components.sensors.schemas import (SensorGetResponse as DefaultSensorGetResponse,
                                                     SensorListResponse as DefaultSensorListResponse)


class SensorModel(Schema):
    model_config = ConfigDict(populate_by_name=True)

    sensor_model_name: str = Field(..., alias='sensorModelName')
    sensor_model_url: Union[AnyHttpUrlString, None] = Field(None, alias='sensorModelURL')
    sensor_manufacturer: str = Field(..., alias='sensorManufacturer')


sensorEncodingTypes = Literal[
    'application/pdf',
    'http://www.opengis.net/doc/IS/SensorML/2.0',
    'text/html',
    'application/json'
]


class SensorProperties(Schema):
    model_config = ConfigDict(populate_by_name=True)

    method_code: Union[str, None] = Field(None, alias='methodCode')
    method_type: str = Field(..., alias='methodType')
    method_link: Union[AnyHttpUrlString, None] = Field(None, alias='methodLink')
    sensor_model: SensorModel = Field(..., alias='sensorModel')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')


class SensorGetResponse(DefaultSensorGetResponse):
    encoding_type: sensorEncodingTypes = Field(..., alias='encodingType')
    sensor_metadata: SensorProperties = Field(..., alias='metadata')


class SensorListResponse(DefaultSensorListResponse):
    value: List[SensorGetResponse]
