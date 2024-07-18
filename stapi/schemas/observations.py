from uuid import UUID
from ninja import Schema, Field
from typing import List, Union, Optional
from sensorthings.types import ISOTimeString, ISOIntervalString
from sensorthings.components.observations.schemas import ObservationPostBody as DefaultObservationPostBody
from sensorthings.extensions.dataarray.schemas import (ObservationGetResponse as DefaultObservationGetResponse,
                                                       ObservationListResponse as DefaultObservationListResponse,
                                                       ObservationDataArrayResponse as
                                                       DefaultObservationDataArrayResponse,
                                                       ObservationDataArrayPostBody as
                                                       DefaultObservationDataArrayPostBody)


class ResultQualifier(Schema):
    code: str
    description: str


class ObservationResultQualityResponse(Schema):
    quality_code: Optional[str] = Field(None, alias='qualityCode')
    result_qualifiers: List[ResultQualifier] = Field(None, alias='resultQualifiers')

    class Config:
        populate_by_name = True


class ObservationResultQualityBody(Schema):
    quality_code: Optional[str] = Field(None, alias='qualityCode')
    result_qualifiers: List[UUID] = Field(None, alias='resultQualifiers')


dataArrayList = List[List[Union[UUID, float, ISOTimeString, ISOIntervalString, ObservationResultQualityResponse, dict]]]
dataArrayPost = List[List[Union[UUID, float, ISOTimeString, ISOIntervalString, ObservationResultQualityBody, dict]]]


class ObservationDataArrayResponse(DefaultObservationDataArrayResponse):
    data_array: dataArrayList = Field(..., alias='dataArray')

    class Config:
        populate_by_name = True


class ObservationGetResponse(DefaultObservationGetResponse):
    result_quality: ObservationResultQualityResponse = Field(None, alias='resultQuality')


class ObservationListResponse(DefaultObservationListResponse):
    value: Union[List[ObservationGetResponse], List[ObservationDataArrayResponse]]


class ObservationPostBody(DefaultObservationPostBody):
    result_quality: ObservationResultQualityBody = Field(None, alias='resultQuality')


class ObservationDataArrayPostBody(DefaultObservationDataArrayPostBody):
    data_array: dataArrayPost = Field(..., alias='dataArray')
