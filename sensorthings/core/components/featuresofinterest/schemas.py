from typing import TYPE_CHECKING, Literal
from pydantic import Field, HttpUrl
from geojson_pydantic import Feature
from ninja import Schema
from sensorthings.core.schemas import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, NestedEntity
from sensorthings.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.core.components.observations.schemas import Observation


featureEncodingTypes = Literal['application/geo+json']


class FeatureOfInterestFields(Schema):
    name: str
    description: str
    encoding_type: featureEncodingTypes = Field(..., alias='encodingType')
    feature: Feature
    properties: dict = {}


class FeatureOfInterestRelations(Schema):
    observations: list['Observation'] = []


class FeatureOfInterest(FeatureOfInterestFields, FeatureOfInterestRelations):
    pass


class FeatureOfInterestPostBody(BasePostBody, FeatureOfInterestFields):
    observations: list[NestedEntity] = Field(
        [], alias='Observations', nested_class='ObservationPostBody'
    )


@allow_partial
class FeatureOfInterestPatchBody(FeatureOfInterestFields, BasePatchBody):
    pass


class FeatureOfInterestGetResponse(BaseGetResponse, FeatureOfInterestFields):
    observations_link: HttpUrl = Field(..., alias='Observations@iot.navigationLink')


class FeatureOfInterestListResponse(BaseListResponse):
    value: list[FeatureOfInterestGetResponse]
