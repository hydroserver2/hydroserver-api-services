from ninja import Schema
from uuid import UUID
from typing import Optional
from core.schemas import BasePostBody, BasePatchBody


class UnitID(Schema):
    id: UUID


class UnitFields(Schema):
    name: str
    symbol: str
    definition: str
    type: str


class UnitGetResponse(UnitFields, UnitID):
    owner: Optional[str]

    @classmethod
    def serialize(cls, unit):  # Temporary until after Pydantic v2 update
        return {
            'id': unit.id,
            'owner': unit.person.email if unit.person else None,
            **{field: getattr(unit, field) for field in UnitFields.model_fields.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class UnitPostBody(BasePostBody, UnitFields):
    pass


class UnitPatchBody(BasePatchBody, UnitFields):
    pass
