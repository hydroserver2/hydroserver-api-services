import base64
from ninja import Schema
from pydantic import Field, validator, EmailStr
from sensorthings.validators import allow_partial
from accounts.endpoints.organization.schemas import OrganizationFields, OrganizationPatchBody


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
