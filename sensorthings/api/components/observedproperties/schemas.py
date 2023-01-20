from typing import TYPE_CHECKING
from pydantic import Field, HttpUrl
from ninja import Schema
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, NestedEntity
from sensorthings.api.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.api.components.datastreams.schemas import Datastream


class ObservedPropertyFields(Schema):
    name: str
    definition: HttpUrl
    description: str
    properties: dict = {}


class ObservedPropertyRelations(Schema):
    datastreams: list['Datastream'] = []


class ObservedProperty(ObservedPropertyFields, ObservedPropertyRelations):
    pass


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    datastreams: list[NestedEntity] = Field(
        [], alias='Datastreams', nested_class='DatastreamPostBody'
    )


@allow_partial
class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    pass


class ObservedPropertyGetResponse(BaseGetResponse, ObservedPropertyFields):
    datastreams_link: HttpUrl = Field(..., alias='Datastreams@iot.navigationLink')


class ObservedPropertyListResponse(BaseListResponse):
    value: list[ObservedPropertyGetResponse]