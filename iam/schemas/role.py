import uuid
from ninja import Schema, Field
from typing import Optional
from hydroserver.schemas import BaseGetResponse


class RoleFields(Schema):
    name: str = Field(..., max_length=255)
    description: str


class RoleGetResponse(BaseGetResponse, RoleFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
