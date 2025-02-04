import uuid
from ninja import Schema, Field
from pydantic import EmailStr
from django.contrib.auth import get_user_model
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from iam.models import Workspace


User = get_user_model()


class WorkspaceFields(Schema):
    name: str = Field(..., max_length=255)
    private: bool


class WorkspaceGetResponse(BaseGetResponse, WorkspaceFields):
    id: uuid.UUID
    owner: EmailStr = Field(..., validation_alias="owner.username")


class WorkspacePostBody(BasePostBody, WorkspaceFields):
    pass


class WorkspacePatchBody(BasePatchBody, WorkspaceFields):
    pass


class WorkspaceTransferBody(BasePostBody):
    new_owner: EmailStr
