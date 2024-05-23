from ninja import Schema
from pydantic import Field
from uuid import UUID
from typing import Optional
from sensorthings.validators import disable_required_field_validation
from core.schemas import BasePostBody, BasePatchBody


class SensorID(Schema):
    id: UUID


class SensorFields(Schema):
    name: str
    description: str
    encoding_type: str = Field(alias='encodingType')
    manufacturer: str = None
    model: str = None
    model_link: str = Field(None, alias='modelLink')
    method_type: str = Field(alias='methodType')
    method_link: str = Field(None, alias='methodLink')
    method_code: str = Field(None, alias='methodCode')


class SensorGetResponse(SensorFields, SensorID):
    owner: Optional[str]

    @classmethod
    def serialize(cls, sensor):  # Temporary until after Pydantic v2 update
        return {
            'id': sensor.id,
            'owner': sensor.person.email if sensor.person else None,
            **{field: getattr(sensor, field) for field in SensorFields.model_fields.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class SensorPostBody(BasePostBody, SensorFields):
    pass


@disable_required_field_validation
class SensorPatchBody(BasePatchBody, SensorFields):
    pass
