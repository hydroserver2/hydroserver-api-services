from ninja import Schema, Field
from pydantic import EmailStr
from typing import List, Optional, Literal
from django.contrib.auth import get_user_model
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody

User = get_user_model()


class OrganizationFields(Schema):
    code: str = Field(..., max_length=255)
    name: str = Field(..., max_length=30)
    description: Optional[str] = None
    link: Optional[str] = Field(None, max_length=2000)
    organization_type: str = Field(..., max_length=255, alias="type")


class OrganizationGetResponse(BaseGetResponse, OrganizationFields):
    pass


class OrganizationPostBody(BasePostBody, OrganizationFields):
    pass


class OrganizationPatchBody(BasePatchBody, OrganizationFields):
    pass


class UserContactFields(Schema):
    phone: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=255)
    link: Optional[str] = Field(None, max_length=2000)
    user_type: str = Field(..., max_length=255, alias="type")


class UserFields(UserContactFields):
    first_name: str = Field(..., max_length=30)
    middle_name: Optional[str] = Field(None, max_length=30)
    last_name: str = Field(..., max_length=150)
    organization: Optional[OrganizationGetResponse] = None


class AccountContactGetResponse(BaseGetResponse, UserContactFields):
    name: str = Field(..., max_length=255)
    email: EmailStr
    organization_name: Optional[str] = None


class AccountGetResponse(BaseGetResponse, UserFields):
    email: EmailStr
    account_type: Literal["admin", "standard", "limited"]


class AccountPostBody(BasePostBody, UserFields):
    email: EmailStr
    password: str
    organization: Optional[OrganizationPostBody] = None


class AccountPatchBody(BasePatchBody, UserFields):
    organization: Optional[OrganizationPatchBody] = None


class TypeGetResponse(BaseGetResponse):
    user_types: List[str]
    organization_types: List[str]
