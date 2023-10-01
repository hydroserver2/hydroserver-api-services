from ninja import Schema
from pydantic import Field
from uuid import UUID
from sensorthings.validators import allow_partial
from accounts.schemas import UserFields


class SensorID(Schema):
    id: UUID


class SensorFields(Schema):
    name: str
    description: str
    encoding_type: str = Field(alias="encodingType")
    manufacturer: str = None
    model: str = None
    model_link: str = Field(None, alias='modelLink')
    method_type: str = Field(alias='methodType')
    method_link: str = Field(None, alias='methodLink')
    method_code: str = Field(None, alias='methodCode')


class SensorGetResponse(SensorFields, SensorID):
    owner: UserFields

    class Config:
        allow_population_by_field_name = True


class SensorPostBody(SensorFields):
    pass


@allow_partial
class SensorPatchBody(SensorFields):
    pass
