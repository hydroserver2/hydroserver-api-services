from ninja import Schema
from typing import Literal, Optional, TYPE_CHECKING
from pydantic import EmailStr
from api.schemas import BasePostBody
from iam.schemas.account import UserFields

if TYPE_CHECKING:
    from iam.schemas import OrganizationPostBody


class ProviderRedirectPostForm(Schema):
    provider: str
    callback_url: str
    process: Literal["login", "connect"]


class ProviderSignupPostBody(BasePostBody, UserFields):
    email: EmailStr
    organization: Optional["OrganizationPostBody"]
