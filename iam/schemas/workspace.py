import uuid
from typing import Optional
from ninja import Schema, Field
from pydantic import EmailStr
from django.contrib.auth import get_user_model
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from .account import AccountContactGetResponse
from .role import RoleGetResponse

User = get_user_model()


class WorkspaceFields(Schema):
    name: str = Field(..., max_length=255)
    is_private: bool


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
