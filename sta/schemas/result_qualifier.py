import uuid
from typing import Optional, Literal, TYPE_CHECKING
from ninja import Schema, Field, Query
from api.schemas import (
    BaseDetailResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceDetailResponse


class ResultQualifierFields(Schema):
    code: str = Field(..., max_length=255)
    description: str


_order_by_fields = (
    "code",
)

ResultQualifierOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class ResultQualifierQueryParameters(CollectionQueryParameters):
    order_by: Optional[list[ResultQualifierOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by workspace ID."
    )


class ResultQualifierSummaryResponse(BaseDetailResponse, ResultQualifierFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None


class ResultQualifierDetailResponse(BaseDetailResponse, ResultQualifierFields):
    id: uuid.UUID
    workspace: Optional["WorkspaceDetailResponse"] = None


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    workspace_id: Optional[uuid.UUID] = None


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
