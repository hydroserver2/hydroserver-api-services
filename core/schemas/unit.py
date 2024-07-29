from ninja import Schema, Field
from pydantic import AliasChoices, AliasPath
from uuid import UUID
from typing import Optional
from hydroserver.schemas import BasePostBody, BasePatchBody


class UnitID(Schema):
    id: UUID


class UnitFields(Schema):
    name: str
    symbol: str
    definition: str
    type: str


class UnitGetResponse(UnitFields, UnitID):
    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )

    class Config:
        allow_population_by_field_name = True


class UnitPostBody(BasePostBody, UnitFields):
    pass


class UnitPatchBody(BasePatchBody, UnitFields):
    pass
