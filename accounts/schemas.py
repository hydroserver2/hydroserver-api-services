import base64
from ninja import Schema
from datetime import datetime
from typing import Optional
from pydantic import Field, validator, EmailStr
from uuid import UUID
from sensorthings.validators import allow_partial


class OrganizationFields(Schema):
    code: str
    name: str
    description: str = None
    type: str
    link: str = None

    @classmethod
    def is_empty(cls, obj):
        return not (obj.name and obj.code and obj.type)


class UserFields(Schema):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: EmailStr = None
    middle_name: str = Field(default=None, alias="middleName")
    phone: str = None
    address: str = None
    type: str = None
    link: str = None
    organization: OrganizationFields = None
    hydroshare_connected: bool = Field(default=False, alias="hydroShareConnected")

    class Config:
        allow_population_by_field_name = True


class UserGetResponse(UserFields):
    is_verified: bool = Field(alias="isVerified")


class UserAuthResponse(Schema):
    access: str
    refresh: str
    user: UserGetResponse


class UserPostBody(UserFields):
    password: str


@allow_partial
class OrganizationPatchBody(OrganizationFields):
    pass


@allow_partial
class UserPatchBody(UserFields):
    organization: OrganizationPatchBody = None


class VerifyAccountPostBody(Schema):
    uid: str
    token: str

    @validator('uid')
    def decode_uid(cls, v: str):
        return base64.b64decode(v).decode('utf-8')


class PasswordResetRequestPostBody(Schema):
    email: str


class ResetPasswordPostBody(Schema):
    uid: str
    token: str
    password: str


class APIKeyFields(Schema):
    name: str
    scope: str
    permissions: Optional[dict]
    expires: Optional[datetime]


class APIKeyGetResponse(APIKeyFields):
    id: UUID


class APIKeyPostBody(APIKeyFields):
    pass


@allow_partial
class APIKeyPatchBody(APIKeyFields):
    pass


class APIKeyPostResponse(APIKeyGetResponse):
    key: str
