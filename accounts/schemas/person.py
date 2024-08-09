import base64
from ninja import Schema
from typing import Optional, Annotated
from pydantic import Field, field_validator, EmailStr, AliasChoices, StringConstraints as StrCon
from accounts.schemas.organization import OrganizationFields, OrganizationPatchBody
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class PersonFields(Schema):
    first_name: Annotated[str, StrCon(strip_whitespace=True, max_length=150)]
    last_name: Annotated[str, StrCon(strip_whitespace=True, max_length=150)]
    user_email: Optional[EmailStr] = Field(
        None, serialization_alias='email',
        validation_alias=AliasChoices('email', 'user_email'),
    )
    middle_name: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=50)]] = None
    phone: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=15)]] = None
    address: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    type: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=2000)]] = None
    organization: Optional[OrganizationFields] = None

    class Config:
        allow_population_by_field_name = True


class PersonGetResponse(BaseGetResponse, PersonFields):
    is_verified: bool
    hydroshare_connected: Optional[bool] = Field(
        False, serialization_alias='hydroShareConnected',
        validation_alias=AliasChoices('hydroShareConnected', 'hydroshare_connected'),
    )


class PersonAuthResponse(BaseGetResponse, Schema):
    access: str
    refresh: str
    user: PersonGetResponse


class PersonPostBody(BasePostBody, PersonFields):
    password: str


class PersonPatchBody(BasePatchBody, PersonFields):
    organization: Optional[OrganizationPatchBody] = None


class VerifyAccountPostBody(BasePostBody, Schema):
    uid: str
    token: str

    @field_validator('uid')
    def decode_uid(cls, v: str):
        return base64.b64decode(v).decode('utf-8')


class PasswordResetRequestPostBody(BasePostBody, Schema):
    email: str


class ResetPasswordPostBody(BasePostBody, Schema):
    uid: str
    token: str
    password: str
