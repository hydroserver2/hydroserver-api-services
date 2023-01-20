from typing import TYPE_CHECKING, Literal
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, EntityId, NestedEntity
from sensorthings.api.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.api.components.things.schemas import Thing
    from sensorthings.api.components.historicallocations.schemas import HistoricalLocation


locationEncodingTypes = Literal['application/geo+json']


class LocationFields(Schema):
    name: str
    description: str
    encoding_type: locationEncodingTypes = Field(..., alias='encodingType')
    location: dict
    properties: dict = {}


class LocationRelations(Schema):
    things: list['Thing'] = []
    historical_locations: list['HistoricalLocation'] = []


class Location(LocationFields, LocationRelations):
    pass


class LocationPostBody(BasePostBody, LocationFields):
    things: list[EntityId | NestedEntity] = Field(
        [], alias='Things', nested_class='ThingPostBody'
    )
    historical_locations: list[EntityId | NestedEntity] = Field(
        [], alias='HistoricalLocations', nested_class='HistoricalLocationPostBody'
    )


@allow_partial
class LocationPatchBody(LocationFields, BasePatchBody):
    things: list[EntityId] = Field([], alias='Things')
    historical_locations: list[EntityId] = Field([], alias='HistoricalLocations')


class LocationGetResponse(BaseGetResponse, LocationFields):
    things_link: HttpUrl = Field(..., alias='Things@iot.navigationLink')
    historical_locations_link: HttpUrl = Field(..., alias='HistoricalLocations@iot.navigationLink')


class LocationListResponse(BaseListResponse):
    value: list[LocationGetResponse]
