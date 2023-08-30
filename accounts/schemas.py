import base64
from ninja import Schema
from pydantic import validator
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
    first_name: str
    last_name: str
    email: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str = None
    link: str = None
    organization: OrganizationFields = None


class UserGetResponse(UserFields):
    is_verified: bool


class UserAuthResponse(Schema):
    access: str
    refresh: str
    user: UserGetResponse


class UserPostBody(UserFields):
    password: str


@allow_partial
class UserPatchBody(UserFields):
    pass


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
