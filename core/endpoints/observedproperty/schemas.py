from ninja import Schema
from uuid import UUID
from sensorthings.validators import allow_partial
from accounts.schemas import UserFields


class ObservedPropertyID(Schema):
    id: UUID


class ObservedPropertyFields(Schema):
    name: str
    definition: str
    description: str = None
    type: str = None
    code: str = None


class ObservedPropertyGetResponse(ObservedPropertyFields, ObservedPropertyID):
    owner: UserFields

    class Config:
        allow_population_by_field_name = True


class ObservedPropertyPostBody(ObservedPropertyFields):
    pass


@allow_partial
class ObservedPropertyPatchBody(ObservedPropertyFields):
    pass
