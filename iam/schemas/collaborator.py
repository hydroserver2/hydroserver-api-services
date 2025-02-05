import uuid
from ninja import Field
from pydantic import EmailStr
from hydroserver.schemas import BaseGetResponse, BasePostBody


class CollaboratorGetResponse(BaseGetResponse):
    email: EmailStr = Field(..., validation_alias="user.email")
    role_id: uuid.UUID


class CollaboratorPostBody(BasePostBody):
    email: EmailStr
    role_id: uuid.UUID


class CollaboratorDeleteBody(BasePostBody):
    email: EmailStr
