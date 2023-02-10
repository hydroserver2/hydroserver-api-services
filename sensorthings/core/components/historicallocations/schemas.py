from typing import TYPE_CHECKING
from datetime import datetime
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.core.schemas import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, EntityId, \
    NestedEntity
from sensorthings.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.core.components.things.schemas import Thing
    from sensorthings.core.components.locations.schemas import Location


class HistoricalLocationFields(Schema):
    time: datetime


class HistoricalLocationRelations(Schema):
    thing: 'Thing'
    locations: list['Location']


class HistoricalLocation(HistoricalLocationFields, HistoricalLocationRelations):
    pass


class HistoricalLocationPostBody(BasePostBody, HistoricalLocationFields):
    thing: EntityId | NestedEntity = Field(
        ..., alias='Thing', nested_class='ThingPostBody'
    )
    locations: list[EntityId | NestedEntity] = Field(
        ..., alias='Locations', nested_class='LocationPostBody'
    )


@allow_partial
class HistoricalLocationPatchBody(HistoricalLocationFields, BasePatchBody):
    thing: EntityId = Field(..., alias='Thing')
    locations: list[EntityId] = Field(..., alias='Locations')


class HistoricalLocationGetResponse(BaseGetResponse, HistoricalLocationFields):
    thing_link: HttpUrl = Field(..., alias='Thing@iot.navigationLink')
    historical_locations_link: HttpUrl = Field(..., alias='Locations@iot.navigationLink')


class HistoricalLocationListResponse(BaseListResponse):
    value: list[HistoricalLocationGetResponse]
