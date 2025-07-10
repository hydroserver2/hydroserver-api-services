import uuid
from typing import Optional, Literal, TYPE_CHECKING
from datetime import datetime
from ninja import Schema, Field, Query
from api.schemas import BaseDetailResponse, BasePostBody, BasePatchBody, CollectionQueryParameters

if TYPE_CHECKING:
    from iam.schemas import RoleDetailResponse


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
    role_id: list[uuid.UUID] = Query(
        [], description="Filter API keys by role ID."
    )


class APIKeyGetFields(APIKeyFields):
    workspace_id: Optional[uuid.UUID]
    role: "RoleDetailResponse"
    created_at: datetime
    last_used: Optional[datetime]


class APIKeyDetailResponse(BaseDetailResponse, APIKeyGetFields):
    id: uuid.UUID


class APIKeyPostResponse(BaseDetailResponse, APIKeyGetFields):
    id: uuid.UUID
    key: str = Field(..., max_length=255)


class APIKeyPostBody(BasePostBody, APIKeyFields):
    role_id: uuid.UUID


class APIKeyPatchBody(BasePatchBody, APIKeyFields):
    role_id: Optional[uuid.UUID] = None
