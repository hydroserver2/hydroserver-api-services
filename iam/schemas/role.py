import uuid
from ninja import Schema, Field
from typing import Optional, Literal
from hydroserver.schemas import BaseGetResponse
from iam.models.permission import PERMISSION_CHOICES, RESOURCE_TYPE_CHOICES

RESOURCE_TYPES = Literal[*[choice[0] for choice in RESOURCE_TYPE_CHOICES]]
PERMISSIONS = Literal[*[choice[0] for choice in PERMISSION_CHOICES]]


class PermissionFields(Schema):
    resource: RESOURCE_TYPES = Field(..., validation_alias="resource_type")
    action: PERMISSIONS = Field(..., validation_alias="permission_type")


class PermissionGetResponse(BaseGetResponse, PermissionFields):
    pass


class RoleFields(Schema):
    name: str = Field(..., max_length=255)
    description: str


class RoleGetResponse(BaseGetResponse, RoleFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    permissions: list[PermissionGetResponse]
