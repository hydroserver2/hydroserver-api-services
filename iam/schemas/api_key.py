import uuid
from typing import Optional, Literal, TYPE_CHECKING
from datetime import datetime
from ninja import Schema, Field, Query
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceSummaryResponse, RoleSummaryResponse


class APIKeyFields(Schema):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None


_order_by_fields = (
    "name",
    "isActive",
    "expiresAt",
)

APIKeyOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class APIKeyQueryParameters(CollectionQueryParameters):
    expand_related: Optional[bool] = None
    order_by: Optional[list[APIKeyOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    role_id: list[uuid.UUID] = Query([], description="Filter API keys by role ID.")


class APIKeyGetFields(APIKeyFields):
    created_at: datetime
    last_used: Optional[datetime]


class APIKeySummaryResponse(BaseGetResponse, APIKeyGetFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    role_id: uuid.UUID


class APIKeyDetailResponse(BaseGetResponse, APIKeyGetFields):
    id: uuid.UUID
    workspace: "WorkspaceSummaryResponse"
    role: "RoleSummaryResponse"


class APIKeySummaryPostResponse(APIKeySummaryResponse, APIKeyGetFields):
    key: str = Field(..., max_length=255)


class APIKeyDetailPostResponse(APIKeyDetailResponse, APIKeyGetFields):
    key: str = Field(..., max_length=255)


class APIKeyPostBody(BasePostBody, APIKeyFields):
    role_id: uuid.UUID


class APIKeyPatchBody(BasePatchBody, APIKeyFields):
    role_id: Optional[uuid.UUID] = None
