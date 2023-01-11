from typing import TYPE_CHECKING, Literal
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody

if TYPE_CHECKING:
    from sensorthings.api.entities.things.schemas import Thing


locationEncodingTypes = Literal['application/geo+json']


class LocationFields(Schema):
    name: str
    description: str
    encodingType: locationEncodingTypes
    location: dict
    properties: dict = {}


class LocationRelations(Schema):
    thing: 'list[Thing]' = []


class Location(LocationFields, LocationRelations):
    pass


class LocationPostBody(LocationFields, BasePostBody):
    pass


class LocationPatchBody(BasePatchBody, LocationFields):
    pass


class LocationGetResponse(BaseGetResponse, LocationFields):
    things_link: HttpUrl = Field(..., alias='Things@iot.navigationLink')
    historical_locations_link: HttpUrl = Field(..., alias='HistoricalLocations@iot.navigationLink')


class LocationListResponse(BaseListResponse):
    value: list[LocationGetResponse]
