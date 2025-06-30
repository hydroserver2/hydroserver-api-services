import uuid
from typing import Optional
from ninja import Schema, Field, Query
from pydantic import EmailStr
from django.contrib.auth import get_user_model
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody, CollectionQueryParameters
from .account import AccountContactGetResponse
from .role import RoleGetResponse

User = get_user_model()


class WorkspaceFields(Schema):
    name: str = Field(..., max_length=255)
    is_private: bool


class WorkspaceQueryParameters(CollectionQueryParameters):
    is_associated: Optional[bool] = Query(
        None, description="Whether the workspace is associated with the authenticated user"
    )
    is_private: Optional[bool] = Query(
        None, description="Whether the returned workspaces should be private or public."
    )


class WorkspaceGetResponse(BaseGetResponse, WorkspaceFields):
    id: uuid.UUID
    owner: AccountContactGetResponse
    collaborator_role: Optional[RoleGetResponse] = None
    pending_transfer_to: Optional[AccountContactGetResponse] = None


class WorkspacePostBody(BasePostBody, WorkspaceFields):
    pass


class WorkspacePatchBody(BasePatchBody, WorkspaceFields):
    pass


class WorkspaceTransferBody(BasePostBody):
    new_owner: EmailStr
