import uuid
from typing import Optional, Literal, TYPE_CHECKING
from ninja import Schema, Field, Query
from pydantic import EmailStr
from django.contrib.auth import get_user_model
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import AccountContactDetailResponse, RoleDetailResponse


User = get_user_model()


class WorkspaceFields(Schema):
    name: str = Field(..., max_length=255)
    is_private: bool


_order_by_fields = (
    "name",
    "isPrivate",
)

WorkspaceOrderByFields = Literal[
    *_order_by_fields, *[f"-{f}" for f in _order_by_fields]
]


class WorkspaceQueryParameters(CollectionQueryParameters):
    order_by: Optional[list[WorkspaceOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    is_associated: Optional[bool] = Query(
        None,
        description="Whether the workspace is associated with the authenticated user",
    )
    is_private: Optional[bool] = Query(
        None, description="Whether the returned workspaces should be private or public."
    )


class WorkspaceSummaryResponse(BaseGetResponse, WorkspaceFields):
    id: uuid.UUID


class WorkspaceDetailResponse(BaseGetResponse, WorkspaceFields):
    id: uuid.UUID
    owner: "AccountContactDetailResponse"
    collaborator_role: Optional["RoleDetailResponse"] = None
    pending_transfer_to: Optional["AccountContactDetailResponse"] = None


class WorkspacePostBody(BasePostBody, WorkspaceFields):
    pass


class WorkspacePatchBody(BasePatchBody, WorkspaceFields):
    pass


class WorkspaceTransferBody(BasePostBody):
    new_owner: EmailStr
