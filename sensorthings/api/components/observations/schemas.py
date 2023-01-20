from typing import TYPE_CHECKING, Literal
from pydantic import Field, HttpUrl, validator
from datetime import datetime
from ninja import Schema
from sensorthings.api.core import BaseListResponse, BaseGetResponse, BasePostBody, BasePatchBody, EntityId, NestedEntity
from sensorthings.api.core.iso_types import ISOTime, ISOInterval
from sensorthings.api.core.utils import allow_partial

if TYPE_CHECKING:
    from sensorthings.api.components.datastreams.schemas import Datastream
    from sensorthings.api.components.featuresofinterest.schemas import FeatureOfInterest


observationTypes = Literal[
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CategoryObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_CountObservation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation',
    'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_TruthObservation'
]


class UnitOfMeasurement(Schema):
    name: str
    symbol: str
    definition: HttpUrl


class ObservationFields(Schema):
    phenomenon_time: ISOTime | ISOInterval | None = Field(..., alias='phenomenonTime')
    result: str
    result_time: ISOTime | None = Field(..., alias='resultTime')
    result_quality: str | None = Field(None, alias='resultQuality')
    valid_time: ISOInterval | None = Field(None, alias='validTime')
    parameters: dict = {}


class ObservationRelations(Schema):
    datastream: 'Datastream'
    feature_of_interest: 'FeatureOfInterest'


class Observation(ObservationFields, ObservationRelations):
    pass


class ObservationPostBody(BasePostBody, ObservationFields):
    datastream: EntityId | NestedEntity = Field(
        ..., alias='Datastream', nested_class='DatastreamPostBody'
    )
    feature_of_interest: EntityId | NestedEntity = Field(
        ..., alias='FeatureOfInterest', nested_class='FeatureOfInterestPostBody'
    )


@allow_partial
class ObservationPatchBody(BasePatchBody, ObservationFields):
    datastream: EntityId = Field(..., alias='Datastream')
    feature_of_interest: EntityId = Field(..., alias='FeatureOfInterest')


class ObservationGetResponse(BaseGetResponse, ObservationFields):
    datastream_link: HttpUrl = Field(..., alias='Datastream@iot.navigationLink')
    feature_of_interest_link: HttpUrl = Field(..., alias='FeatureOfInterest@iot.navigationLink')


class ObservationListResponse(BaseListResponse):
    value: list[ObservationGetResponse]
