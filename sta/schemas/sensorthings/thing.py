from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sensorthings.components.things.schemas import (ThingGetResponse as DefaultThingGetResponse,
                                                    ThingListResponse as DefaultThingListResponse)


class ThingProperties(Schema):
    sampling_feature_type: str
    sampling_feature_code: str
    site_type: str

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel)


class ThingGetResponse(DefaultThingGetResponse):
    properties: ThingProperties

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel)


class ThingListResponse(DefaultThingListResponse):
    value: list[ThingGetResponse]
