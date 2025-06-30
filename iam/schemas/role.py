import uuid
from ninja import Schema, Field, Query
from typing import Optional, Literal
from hydroserver.schemas import BaseGetResponse, CollectionQueryParameters
from iam.models.permission import PERMISSION_CHOICES, RESOURCE_TYPE_CHOICES

RESOURCE_TYPES = Literal[*[choice[0] for choice in RESOURCE_TYPE_CHOICES]]
PERMISSIONS = Literal[*[choice[0] for choice in PERMISSION_CHOICES]]


class PermissionFields(Schema):
    resource: RESOURCE_TYPES = Field(..., validation_alias="resource_type")
    action: PERMISSIONS = Field(..., validation_alias="permission_type")


class RoleQueryParameters(CollectionQueryParameters):
    is_user_role: Optional[bool] = Query(
        None, description="Controls whether the returned roles should be user roles."
    )
    is_apikey_role: Optional[bool] = Query(
        None, description="Controls whether the returned roles should be API key roles."
    )


class PermissionGetResponse(BaseGetResponse, PermissionFields):
    pass


class RoleFields(Schema):
    name: str = Field(..., max_length=255)
    description: str
    is_user_role: bool
    is_apikey_role: bool = Field(..., validation_alias="isAPIKeyRole")


class RoleGetResponse(BaseGetResponse, RoleFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    permissions: list[PermissionGetResponse]
