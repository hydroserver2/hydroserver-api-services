import uuid
from ninja import Schema, Query
from typing import Optional, Literal
from datetime import datetime
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class ObservationFields(Schema):
    phenomenon_time: datetime
    result: float


_order_by_fields = ("phenomenonTime",)

ObservationOrderByFields = Literal[
    *_order_by_fields, *[f"-{f}" for f in _order_by_fields]
]


class ObservationQueryParameters(CollectionQueryParameters):
    order_by: Optional[list[ObservationOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    response_format: Optional[Literal["record", "row", "column"]] = Query(
        None,
        description="Controls the format of the observations response.",
        alias="format",
    )
    phenomenon_time__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum phenomenon time of filtered observations.",
        alias="phenomenon_time_max",
    )
    phenomenon_time__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum phenomenon time of filtered observations.",
        alias="phenomenon_time_min",
    )


class ObservationSummaryResponse(BaseGetResponse, ObservationFields):
    id: uuid.UUID


class ObservationRowResponse(BaseGetResponse):
    fields: list[Literal["phenomenonTime", "result"]]
    data: list[list]


class ObservationColumnarResponse(BaseGetResponse):
    phenomenon_time: list
    result: list


class ObservationPostBody(BasePostBody, ObservationFields):
    pass


class ObservationBulkPostQueryParameters(Schema):
    mode: Optional[Literal["insert", "append", "backfill", "replace"]] = Query(
        None,
        description=(
            "Specifies how new observations are added to the datastream. "
            "`insert` allows observations at any timestamp. "
            "`append` adds only future observations (after the latest existing timestamp). "
            "`backfill` adds only historical observations (before the earliest existing timestamp). "
            "`replace` deletes all observations in the range of provided observations before inserting new ones."
        ),
    )


class ObservationBulkPostBody(BasePostBody):
    fields: list[Literal["phenomenonTime", "result"]]
    data: list[list]


class ObservationPatchBody(BasePatchBody, ObservationFields):
    pass


class ObservationBulkDeleteBody(BasePostBody):
    phenomenon_time_start: Optional[datetime] = None
    phenomenon_time_end: Optional[datetime] = None
