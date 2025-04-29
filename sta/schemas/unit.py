import uuid
from ninja import Schema, Field
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class UnitFields(Schema):
    name: str = Field(..., max_length=255)
    symbol: str = Field(..., max_length=255)
    definition: str
    unit_type: str = Field(..., max_length=255, alias="type")


class UnitGetResponse(BaseGetResponse, UnitFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class UnitPostBody(BasePostBody, UnitFields):
    workspace_id: uuid.UUID


class UnitPatchBody(BasePatchBody, UnitFields):
    pass
