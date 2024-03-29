from ninja import Schema
from pydantic import Field
from uuid import UUID
from typing import Optional
from sensorthings.validators import allow_partial
from core.schemas_old import BasePostBody, BasePatchBody


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
    owner: Optional[str]

    class Config:
        allow_population_by_field_name = True


class SensorPostBody(BasePostBody, SensorFields):
    pass


@allow_partial
class SensorPatchBody(BasePatchBody, SensorFields):
    pass
