import uuid
from typing import Optional, Literal, TYPE_CHECKING
from ninja import Schema, Field, Query
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceSummaryResponse


class ResultQualifierFields(Schema):
    code: str = Field(..., max_length=255)
    description: str


_order_by_fields = ("code",)

ResultQualifierOrderByFields = Literal[
    *_order_by_fields, *[f"-{f}" for f in _order_by_fields]
]


class ResultQualifierQueryParameters(CollectionQueryParameters):
    expand_related: Optional[bool] = None
    order_by: Optional[list[ResultQualifierOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID | Literal["null"]] = Query(
        [], description="Filter sensors by workspace ID."
    )


class ResultQualifierSummaryResponse(BaseGetResponse, ResultQualifierFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class ResultQualifierDetailResponse(BaseGetResponse, ResultQualifierFields):
    id: uuid.UUID
    workspace: Optional["WorkspaceSummaryResponse"]


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    workspace_id: Optional[uuid.UUID] = None


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
