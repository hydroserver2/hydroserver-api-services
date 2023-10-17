from ninja import Schema
from uuid import UUID
from typing import Optional
from sensorthings.validators import allow_partial
from accounts.schemas import UserFields


class UnitID(Schema):
    id: UUID


class UnitFields(Schema):
    name: str
    symbol: str
    definition: str
    type: str


class UnitGetResponse(UnitFields, UnitID):
    owner: Optional[UserFields]

    class Config:
        allow_population_by_field_name = True


class UnitPostBody(UnitFields):
    pass


@allow_partial
class UnitPatchBody(UnitFields):
    pass
