from typing import TYPE_CHECKING
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.core.schemas import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, EntityId, \
    NestedEntity
from sensorthings.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.core.components.locations.schemas import Location
    from sensorthings.core.components.historicallocations.schemas import HistoricalLocation
    from sensorthings.core.components.datastreams.schemas import Datastream


class ThingFields(Schema):
    name: str
    description: str
    properties: dict | None = None


class ThingRelations(Schema):
    locations: list['Location'] = []
    historical_locations: list['HistoricalLocation'] = []
    datastreams: list['Datastream'] = []


class Thing(ThingFields, ThingRelations):
    pass


class ThingPostBody(BasePostBody, ThingFields):
    locations: list[EntityId | NestedEntity] = Field(
        [], alias='Locations', nested_class='LocationPostBody'
    )
    historical_locations: list[NestedEntity] = Field(
        [], alias='HistoricalLocations', nested_class='HistoricalLocationPostBody'
    )
    datastreams: list[NestedEntity] = Field(
        [], alias='Datastreams', nested_class='DatastreamPostBody'
    )


@allow_partial
class ThingPatchBody(BasePatchBody, ThingFields):
    locations: list[EntityId] = Field([], alias='Locations')


class ThingGetResponse(ThingFields, BaseGetResponse):
    locations_link: HttpUrl = Field(..., alias='Locations@iot.navigationLink')
    historical_locations_link: HttpUrl = Field(..., alias='HistoricalLocations@iot.navigationLink')
    datastreams_link: HttpUrl = Field(..., alias='Datastreams@iot.navigationLink')


class ThingListResponse(BaseListResponse):
    value: list[ThingGetResponse]


class ThingGetResponseODM(ThingGetResponse):
    properties: str
