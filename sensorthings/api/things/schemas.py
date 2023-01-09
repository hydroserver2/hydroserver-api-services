from typing import TYPE_CHECKING
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.schemas import BaseEntitiesResponse, BaseEntityResponse


# class ThingResponseBody(Thing, BaseEntityResponse):
#     locations_link: HttpUrl = Field(..., alias='Locations@iot.navigationLink')
#     datastreams_link: HttpUrl = Field(..., alias='Datastreams@iot.navigationLink')
#     historical_locations_link: HttpUrl = Field(..., alias='HistoricalLocations@iot.navigationLink')
#
#
# class ThingsResponseBody(BaseEntitiesResponse):
#     value: list[ThingResponseBody]
