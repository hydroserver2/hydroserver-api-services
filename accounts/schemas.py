import base64
from ninja import Schema
from pydantic import validator
from hydrothings.validators import allow_partial


class UserFields(Schema):
    first_name: str
    last_name: str
    email: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str = None
    organization: str = None
    link: str = None


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
