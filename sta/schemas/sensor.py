import uuid
from typing import Optional
from ninja import Schema, Field
from sta.schemas.sensorthings.sensor import sensorEncodingTypes
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class SensorFields(Schema):
    name: str = Field(..., max_length=255)
    description: str
    encoding_type: sensorEncodingTypes = Field(..., max_length=255)
    manufacturer: Optional[str] = Field(None, max_length=255)
    sensor_model: Optional[str] = Field(None, max_length=255, alias="model")
    sensor_model_link: Optional[str] = Field(None, max_length=500, alias="modelLink")
    method_type: str = Field(..., max_length=100)
    method_link: Optional[str] = Field(None, max_length=500)
    method_code: Optional[str] = Field(None, max_length=50)


class SensorGetResponse(BaseGetResponse, SensorFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class SensorPostBody(BasePostBody, SensorFields):
    workspace_id: uuid.UUID


class SensorPatchBody(BasePatchBody, SensorFields):
    pass
