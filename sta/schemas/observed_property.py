import uuid
from typing import Optional
from ninja import Schema, Field, Query
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class ObservedPropertyFields(Schema):
    name: str = Field(..., max_length=255)
    definition: str
    description: str
    observed_property_type: str = Field(..., max_length=255, alias="type")
    code: str = Field(..., max_length=255)


class ObservedPropertyQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter observed properties by workspace ID."
    )
    thing_id: list[uuid.UUID] = Query(
        [], description="Filter observed properties by thing ID."
    )
    datastream_id: list[uuid.UUID] = Query(
        [], description="Filter observed properties by datastream ID."
    )
    name: list[str] = Query([], description="Filter observed properties by name")
    observed_property_type: list[str] = Query(
        [], description="Filter observed properties by type", alias="type"
    )
    code: list[str] = Query([], description="Filter observed properties by code")


class ObservedPropertyGetResponse(BaseGetResponse, ObservedPropertyFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    workspace_id: uuid.UUID


class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    pass
