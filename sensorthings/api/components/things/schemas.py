from typing import TYPE_CHECKING
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, EntityId, NestedEntity
from sensorthings.api.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.api.components.locations.schemas import Location
    from sensorthings.api.components.historicallocations.schemas import HistoricalLocation
    from sensorthings.api.components.datastreams.schemas import Datastream


class ThingFields(Schema):
    name: str
    description: str
    properties: dict | str = {}


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

