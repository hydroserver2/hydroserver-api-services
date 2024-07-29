from ninja import Schema
from pydantic import Field
from pydantic import AliasChoices, AliasPath
from uuid import UUID
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class SensorID(Schema):
    id: UUID


class SensorFields(Schema):
    name: str
    description: str
    encoding_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    model_link: Optional[str] = None
    method_type: str
    method_link: Optional[str] = None
    method_code: Optional[str] = None


class SensorGetResponse(BaseGetResponse, SensorFields, SensorID):
    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )

    class Config:
        allow_population_by_field_name = True


class SensorPostBody(BasePostBody, SensorFields):
    pass


class SensorPatchBody(BasePatchBody, SensorFields):
    pass
