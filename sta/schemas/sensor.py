import uuid
from typing import Optional
from ninja import Schema, Field, Query
from sta.schemas.sensorthings.sensor import sensorEncodingTypes
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


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


class SensorQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by workspace ID."
    )
    thing_id: list[uuid.UUID] = Query([], description="Filter sensors by thing ID.")
    datastream_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by datastream ID."
    )
    name: list[str] = Query([], description="Filter sensors by name")
    encoding_type: list[str] = Query([], description="Filter sensors by encodingType")
    manufacturer: list[str] = Query([], description="Filter sensors by manufacturer")
    sensor_model: list[str] = Query(
        [], description="Filter sensors by model", alias="model"
    )
    method_type: list[str] = Query([], description="Filter sensors by methodType")
    method_code: list[str] = Query([], description="Filter sensors by methodCode")


class SensorGetResponse(BaseGetResponse, SensorFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class SensorPostBody(BasePostBody, SensorFields):
    workspace_id: uuid.UUID


class SensorPatchBody(BasePatchBody, SensorFields):
    pass
