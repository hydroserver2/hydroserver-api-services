import uuid
from typing import Optional
from datetime import datetime
from ninja import Schema, Field, Query
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody, CollectionQueryParameters
from .role import RoleGetResponse


class APIKeyFields(Schema):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None


class APIKeyQueryParameters(CollectionQueryParameters):
    role_id: list[uuid.UUID] = Query(
        [], description="Filter API keys by role ID."
    )


class APIKeyGetFields(APIKeyFields):
    workspace_id: Optional[uuid.UUID]
    role: RoleGetResponse
    created_at: datetime
    last_used: Optional[datetime]


class APIKeyGetResponse(BaseGetResponse, APIKeyGetFields):
    id: uuid.UUID


class APIKeyPostResponse(BaseGetResponse, APIKeyGetFields):
    id: uuid.UUID
    key: str = Field(..., max_length=255)


class APIKeyPostBody(BasePostBody, APIKeyFields):
    role_id: uuid.UUID


class APIKeyPatchBody(BasePatchBody, APIKeyFields):
    role_id: Optional[uuid.UUID] = None
