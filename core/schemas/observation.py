from ninja import Schema
from pydantic import Field
from typing import List
from uuid import UUID
from datetime import datetime
from sensorthings.validators import allow_partial
from core.schemas_old import BasePostBody, BasePatchBody


class ObservationID(Schema):
    id: UUID


class ObservationFields(Schema):
    datastream_id: UUID = Field(..., alias='datastreamId')
    feature_of_interest_id: UUID = Field(None, alias='featureOfInterestId')
    phenomenon_time: datetime = Field(..., alias='phenomenonTime')
    result: float
    result_time: datetime = Field(None, alias='resultTime')
    quality_code: str = Field(None, alias='qualityCode')
    result_qualifiers: List[UUID] = Field(None, alias='resultQualifiers')


class ObservationGetResponse(ObservationFields, ObservationID):

    class Config:
        allow_population_by_field_name = True


class ObservationPostBody(BasePostBody, ObservationFields):
    pass


@allow_partial
class ObservationPatchBody(BasePatchBody, ObservationFields):
    pass
