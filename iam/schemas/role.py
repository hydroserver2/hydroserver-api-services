import uuid
from ninja import Schema, Field, Query
from typing import Optional, Literal, TYPE_CHECKING
from api.schemas import BaseDetailResponse, CollectionQueryParameters
from iam.models.permission import PERMISSION_CHOICES, RESOURCE_TYPE_CHOICES

if TYPE_CHECKING:
    from iam.schemas import WorkspaceDetailResponse

RESOURCE_TYPES = Literal[*[choice[0] for choice in RESOURCE_TYPE_CHOICES]]
PERMISSIONS = Literal[*[choice[0] for choice in PERMISSION_CHOICES]]


class PermissionFields(Schema):
    resource: RESOURCE_TYPES = Field(..., validation_alias="resource_type")
    action: PERMISSIONS = Field(..., validation_alias="permission_type")


class PermissionDetailResponse(BaseDetailResponse, PermissionFields):
    pass


class RoleFields(Schema):
    name: str = Field(..., max_length=255)
    description: str
    is_user_role: bool
    is_apikey_role: bool = Field(..., validation_alias="isAPIKeyRole")


_order_by_fields = (
    "name",
    "isUserRole",
    "isAPIKeyRole",
)

RoleOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class RoleQueryParameters(CollectionQueryParameters):
    order_by: Optional[list[RoleOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter roless by workspace ID."
    )
    is_user_role: Optional[bool] = Query(
        None, description="Controls whether the returned roles should be user roles."
    )
    is_apikey_role: Optional[bool] = Query(
        None, description="Controls whether the returned roles should be API key roles."
    )


class RoleSummaryResponse(BaseDetailResponse, RoleFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    permissions: list[PermissionDetailResponse]


class RoleDetailResponse(BaseDetailResponse, RoleFields):
    id: uuid.UUID
    workspace: Optional["WorkspaceDetailResponse"] = None
    permissions: list[PermissionDetailResponse]
