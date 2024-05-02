from ninja import Schema
from uuid import UUID
from typing import Optional
from sensorthings.validators import allow_partial
from core.schemas import BasePostBody, BasePatchBody


class ObservedPropertyID(Schema):
    id: UUID


class ObservedPropertyFields(Schema):
    name: str
    definition: str
    description: str = None
    type: str = None
    code: str = None


class ObservedPropertyGetResponse(ObservedPropertyFields, ObservedPropertyID):
    owner: Optional[str]

    @classmethod
    def serialize(cls, observed_property):  # Temporary until after Pydantic v2 update
        return {
            'id': observed_property.id,
            'owner': observed_property.person.email if observed_property.person else None,
            **{field: getattr(observed_property, field) for field in ObservedPropertyFields.__fields__.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    pass


@allow_partial
class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    pass
