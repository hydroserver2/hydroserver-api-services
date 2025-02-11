import uuid
from ninja import Schema, Field
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ObservedPropertyFields(Schema):
    name: str = Field(..., max_length=255)
    definition: str
    description: str
    observed_property_type: str = Field(..., max_length=255, alias="type")
    code: str = Field(..., max_length=255)


class ObservedPropertyGetResponse(BaseGetResponse, ObservedPropertyFields):
    id: uuid.UUID
    workspace_id: uuid.UUID


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    workspace_id: uuid.UUID


class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    pass
