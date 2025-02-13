import uuid
from pydantic import EmailStr
from hydroserver.schemas import BaseGetResponse, BasePostBody
from .role import RoleGetResponse
from .account import AccountContactGetResponse


class CollaboratorGetResponse(BaseGetResponse):
    user: AccountContactGetResponse
    role: RoleGetResponse


class CollaboratorPostBody(BasePostBody):
    email: EmailStr
    role_id: uuid.UUID


class CollaboratorDeleteBody(BasePostBody):
    email: EmailStr
