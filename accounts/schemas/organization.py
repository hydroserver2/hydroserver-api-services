from ninja import Schema
from pydantic import StringConstraints as StrCon
from typing import Optional, Annotated
from hydroserver.schemas import BasePatchBody


class OrganizationFields(Schema):
    code: Annotated[str, StrCon(strip_whitespace=True, max_length=200)]
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=500)]
    description: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=2000)]] = None


class OrganizationPatchBody(BasePatchBody, OrganizationFields):
    pass
