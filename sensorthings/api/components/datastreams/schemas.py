from typing import TYPE_CHECKING, Literal
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, EntityId, NestedEntity
from sensorthings.api.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.api.components.things.schemas import Thing
    from sensorthings.api.components.sensors.schemas import Sensor
    from sensorthings.api.components.observedproperties.schemas import ObservedProperty
    from sensorthings.api.components.observations.schemas import Observation


observationTypes = Literal[
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CategoryObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CountObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_TruthObservation'
]


class UnitOfMeasurement(Schema):
    name: str
    symbol: str
    definition: HttpUrl


# TODO Add validation for temporal duration types.
class DatastreamFields(Schema):
    name: str
    description: str
    unit_of_measurement: UnitOfMeasurement = Field(..., alias='unitOfMeasurement')
    observation_type: observationTypes = Field(..., alias='observationType')
    observed_area: dict = Field({}, alias='observedArea')
    phenomenon_time: str | None = Field(None, alias='phenomenonTime')
    result_time: str | None = Field(None, alias='resultTime')
    properties: dict = {}


class DatastreamRelations(Schema):
    thing: 'Thing'
    sensor: 'Sensor'
    observed_property: 'ObservedProperty'


class Datastream(DatastreamFields, DatastreamRelations):
    pass


class DatastreamPostBody(BasePostBody, DatastreamFields):
    thing: EntityId | NestedEntity = Field(
        ..., alias='Thing', nested_class='ThingPostBody'
    )
    sensor: EntityId | NestedEntity = Field(
        ..., alias='Sensor', nested_class='SensorPostBody'
    )
    observed_property: EntityId | NestedEntity = Field(
        ..., alias='ObservedProperty', nested_class='ObservedPropertyPostBody'
    )


@allow_partial
class DatastreamPatchBody(BasePatchBody, DatastreamFields):
    thing: EntityId = Field(..., alias='Thing')
    sensor: EntityId = Field(..., alias='Sensor')
    observed_property: EntityId = Field(..., alias='ObservedProperty')


class DatastreamGetResponse(BaseGetResponse, DatastreamFields):
    thing_link: HttpUrl = Field(..., alias='Thing@iot.navigationLink')
    sensor_link: HttpUrl = Field(..., alias='Sensor@iot.navigationLink')
    observed_property_link: HttpUrl = Field(..., alias='ObservedProperty@iot.navigationLink')


class DatastreamListResponse(BaseListResponse):
    value: list[DatastreamGetResponse]
