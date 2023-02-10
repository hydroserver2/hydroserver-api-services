from typing import TYPE_CHECKING, Literal
from pydantic import Field, HttpUrl, validator
from ninja import Schema
from sensorthings.core.schemas import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, NestedEntity
from sensorthings.core.utils import allow_partial
from sensorthings.core.components.sensors.utils import metadata_validator

if TYPE_CHECKING:
    from sensorthings.core.components.datastreams.schemas import Datastream


sensorEncodingTypes = Literal[
    'application/pdf',
    'http://www.opengis.net/doc/IS/SensorML/2.0',
    'text/html'
]


class SensorFields(Schema):
    name: str
    description: str
    encoding_type: sensorEncodingTypes = Field(..., alias='encodingType')
    sensor_metadata: str = Field(..., alias='metadata')
    properties: dict = {}

    _metadata_validator = validator('sensor_metadata', allow_reuse=True, check_fields=False)(metadata_validator)


class SensorRelations(Schema):
    datastreams: list['Datastream'] = []


class Sensor(SensorFields, SensorRelations):
    pass


class SensorPostBody(BasePostBody, SensorFields):
    datastreams: list[NestedEntity] = Field(
        [], alias='Datastreams', nested_class='DatastreamPostBody'
    )


@allow_partial
class SensorPatchBody(BasePatchBody, SensorFields):
    pass


class SensorGetResponse(SensorFields, BaseGetResponse):
    datastreams_link: HttpUrl = Field(..., alias='Datastreams@iot.navigationLink')


class SensorListResponse(BaseListResponse):
    value: list[SensorGetResponse]
