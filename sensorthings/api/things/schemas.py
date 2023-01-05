from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.schemas import BaseEntitiesResponse, BaseEntityResponse


class Thing(Schema):
    name: str
    description: str
    properties: dict = {}


class ThingResponseBody(Thing, BaseEntityResponse):
    locations_link: HttpUrl = Field(..., alias='Locations@iot.navigationLink')
    datastreams_link: HttpUrl = Field(..., alias='Datastreams@iot.navigationLink')
    historical_locations_link: HttpUrl = Field(..., alias='HistoricalLocations@iot.navigationLink')


class ThingsResponseBody(BaseEntitiesResponse):
    value: list[ThingResponseBody]
