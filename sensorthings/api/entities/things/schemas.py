from typing import TYPE_CHECKING
from ninja import Schema
from pydantic import Field, HttpUrl
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody
from sensorthings.api.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.api.entities.locations.schemas import Location


class ThingFields(Schema):
    name: str
    description: str
    properties: dict = {}


class ThingRelations(Schema):
    location: 'list[Location]' = []


class Thing(ThingFields, ThingRelations):
    pass


class ThingPostBody(BasePostBody, ThingFields):
    pass


@allow_partial
class ThingPatchBody(BasePatchBody, ThingFields):
    pass


class ThingGetResponse(ThingFields, BaseGetResponse):
    locations_link: HttpUrl = Field(..., alias='Locations@iot.navigationLink')
    datastreams_link: HttpUrl = Field(..., alias='Datastreams@iot.navigationLink')
    historical_locations_link: HttpUrl = Field(..., alias='HistoricalLocations@iot.navigationLink')


class ThingListResponse(BaseListResponse):
    value: list[ThingGetResponse]
