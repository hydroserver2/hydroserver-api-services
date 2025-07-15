import uuid
from typing import Optional, Literal, TYPE_CHECKING
from ninja import Schema, Field, Query
from sta.schemas.sensorthings.sensor import sensorEncodingTypes
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceDetailResponse


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


_order_by_fields = (
    "name",
    "encodingType",
    "manufacturer",
    "model",
    "methodType",
    "methodCode",
)

SensorOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class SensorQueryParameters(CollectionQueryParameters):
    order_by: Optional[list[SensorOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID | Literal["null"]] = Query(
        [], description="Filter sensors by workspace ID."
    )
    datastreams__thing_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by thing ID.", alias="thing_id"
    )
    datastreams__id: list[uuid.UUID] = Query(
        [], description="Filter sensors by datastream ID.", alias="datastream_id"
    )
    encoding_type: list[str] = Query([], description="Filter sensors by encodingType")
    manufacturer: list[str] = Query([], description="Filter sensors by manufacturer")
    method_type: list[str] = Query([], description="Filter sensors by methodType")


class SensorSummaryResponse(BaseGetResponse, SensorFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None


class SensorDetailResponse(BaseGetResponse, SensorFields):
    id: uuid.UUID
    workspace: Optional["WorkspaceDetailResponse"] = None


class SensorPostBody(BasePostBody, SensorFields):
    workspace_id: Optional[uuid.UUID] = None


class SensorPatchBody(BasePatchBody, SensorFields):
    pass
