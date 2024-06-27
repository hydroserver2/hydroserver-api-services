from ninja import Schema
from typing import Optional
from hydroserver.schemas import BasePatchBody


class OrganizationFields(Schema):
    code: str
    name: str
    description: Optional[str] = None
    type: str
    link: Optional[str] = None


class OrganizationPatchBody(BasePatchBody, OrganizationFields):
    pass
