import uuid
from ninja import Schema, Field, Query
from typing import Optional
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)
from iam.schemas import WorkspaceGetResponse


class UnitFields(Schema):
    name: str = Field(..., max_length=255)
    symbol: str = Field(..., max_length=255)
    definition: str
    unit_type: str = Field(..., max_length=255, alias="type")


class UnitQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter units by workspace ID."
    )
    thing_id: list[uuid.UUID] = Query([], description="Filter units by thing ID.")
    datastream_id: list[uuid.UUID] = Query(
        [], description="Filter units by datastream ID."
    )
    name: list[str] = Query([], description="Filter units by name")
    symbol: list[str] = Query([], description="Filter units by symbol")
    unit_type: list[str] = Query([], description="Filter units by type")


class UnitCollectionResponse(BaseGetResponse, UnitFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class UnitGetResponse(BaseGetResponse, UnitFields):
    id: uuid.UUID
    workspace: Optional[WorkspaceGetResponse]


class UnitPostBody(BasePostBody, UnitFields):
    workspace_id: uuid.UUID


class UnitPatchBody(BasePatchBody, UnitFields):
    pass
