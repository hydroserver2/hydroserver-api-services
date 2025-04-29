from ninja import Schema
from typing import Literal, Optional
from pydantic import EmailStr
from hydroserver.schemas import BasePostBody
from .account import UserFields, OrganizationPostBody


class ProviderRedirectPostForm(Schema):
    provider: str
    callback_url: str
    process: Literal["login", "connect"]


class ProviderSignupPostBody(BasePostBody, UserFields):
    email: EmailStr
    organization: Optional[OrganizationPostBody] = None
