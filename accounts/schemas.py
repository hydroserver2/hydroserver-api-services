import base64
from ninja import Schema
from pydantic import validator


class UserFields(Schema):
    first_name: str
    last_name: str
    email: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str = None
    organization: str = None


class UserGetResponse(UserFields):
    is_verified: bool


class UserPostBody(UserFields):
    password: str


class UserPatchBody(UserFields):
    pass


class VerifyAccountPostBody(Schema):
    uid: str
    token: str

    @validator('uid')
    def decode_uid(cls, v: str):
        return base64.b64decode(v).decode('utf-8')
