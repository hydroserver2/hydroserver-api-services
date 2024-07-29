from ninja import Schema, Field
from pydantic import AliasChoices, AliasPath
from uuid import UUID
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ObservedPropertyID(Schema):
    id: UUID


class ObservedPropertyFields(Schema):
    name: str
    definition: str
    description: Optional[str] = None
    type: Optional[str] = None
    code: Optional[str] = None


class ObservedPropertyGetResponse(BaseGetResponse, ObservedPropertyFields, ObservedPropertyID):
    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )

    class Config:
        allow_population_by_field_name = True


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    pass


class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    pass
