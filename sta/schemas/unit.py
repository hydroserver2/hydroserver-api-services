import uuid
from ninja import Schema, Field, Query
from typing import Optional, Literal, TYPE_CHECKING
from api.schemas import (
    BaseDetailResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceDetailResponse


class UnitFields(Schema):
    name: str = Field(..., max_length=255)
    symbol: str = Field(..., max_length=255)
    definition: str
    unit_type: str = Field(..., max_length=255, alias="type")


_order_by_fields = (
    "name",
    "symbol",
    "type",
)

UnitOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class UnitQueryParameters(CollectionQueryParameters):
    order_by: Optional[list[UnitOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter units by workspace ID."
    )
    datastreams__thing_id: list[uuid.UUID] = Query([], description="Filter units by thing ID.", alias="thing_id")
    datastreams__id: list[uuid.UUID] = Query(
        [], description="Filter units by datastream ID.", alias="datastream_id"
    )
    unit_type: list[str] = Query([], description="Filter units by type")


class UnitSummaryResponse(BaseDetailResponse, UnitFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None


class UnitDetailResponse(BaseDetailResponse, UnitFields):
    id: uuid.UUID
    workspace: Optional["WorkspaceDetailResponse"] = None


class UnitPostBody(BasePostBody, UnitFields):
    workspace_id: Optional[uuid.UUID] = None


class UnitPatchBody(BasePatchBody, UnitFields):
    pass
