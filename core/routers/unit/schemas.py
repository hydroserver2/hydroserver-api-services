from ninja import Schema
from pydantic import Field
from uuid import UUID
from sensorthings.validators import allow_partial


class UnitID(Schema):
    id: UUID


class UnitFields(Schema):
    name: str
    symbol: str
    definition: str
    type: str


class UnitGetResponse(UnitFields, UnitID):
    pass

    class Config:
        allow_population_by_field_name = True


class UnitPostBody(UnitFields):
    pass


@allow_partial
class UnitPatchBody(UnitFields):
    pass
