from ninja import Schema, Field
from pydantic import AliasChoices, AliasPath, StringConstraints as StrCon
from uuid import UUID
from typing import Optional, Annotated
from hydroserver.schemas import BasePostBody, BasePatchBody


class UnitID(Schema):
    id: UUID


class UnitFields(Schema):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    symbol: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    definition: Annotated[str, StrCon(strip_whitespace=True)]
    type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]


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
