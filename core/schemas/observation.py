from ninja import Schema
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ObservationID(Schema):
    id: UUID


class ObservationFields(Schema):
    datastream_id: UUID
    feature_of_interest_id: Optional[UUID] = None
    phenomenon_time: datetime
    result: float
    result_time: Optional[datetime] = None
    quality_code: Optional[str] = None
    result_qualifiers: List[UUID] = None


class ObservationGetResponse(BaseGetResponse, ObservationFields, ObservationID):

    class Config:
        allow_population_by_field_name = True


class ObservationPostBody(BasePostBody, ObservationFields):
    pass


class ObservationPatchBody(BasePatchBody, ObservationFields):
    pass
