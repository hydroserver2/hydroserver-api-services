import uuid
from typing import Optional, Literal
from datetime import datetime
from ninja import Schema, Field, Query
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class OrchestrationConfigurationScheduleFields(Schema):
    interval: Optional[int] = Field(None, gt=0)
    interval_units: Optional[Literal["minutes", "hours", "days"]] = None
    crontab: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class OrchestrationConfigurationScheduleDetailResponse(
    BaseGetResponse, OrchestrationConfigurationScheduleFields
):
    pass


_order_by_fields = ("name", "startTime", "endTime")

OrchestrationConfigurationOrderByFields = Literal[
    *_order_by_fields, *[f"-{f}" for f in _order_by_fields]
]


class OrchestrationConfigurationQueryParameters(CollectionQueryParameters):
    expand_related: Optional[bool] = None
    order_by: Optional[list[OrchestrationConfigurationOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID] = Query([], description="Filter by workspace ID.")
    orchestration_system_id: list[uuid.UUID] = Query(
        [], description="Filter by orchestration system ID."
    )
    datastreams__id: list[uuid.UUID] = Query(
        [], description="Filter by associated datastream ID.", alias="datastream_id"
    )
    last_run_successful: Optional[bool] = Query(
        None,
        description="Filters by whether the previous job ran successfully.",
    )
    last_run__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum last run time of filtered datastreams.",
        alias="last_run_max",
    )
    last_run__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum last run time of filtered datastreams.",
        alias="last_run_min",
    )
    next_run__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum next run time of filtered datastreams.",
        alias="next_run_max",
    )
    next_run__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum next run time of filtered datastreams.",
        alias="next_run_min",
    )


class OrchestrationConfigurationSchedulePostBody(
    BasePostBody, OrchestrationConfigurationScheduleFields
):
    pass


class OrchestrationConfigurationSchedulePatchBody(
    BasePatchBody, OrchestrationConfigurationScheduleFields
):
    pass


class OrchestrationConfigurationStatusFields(Schema):
    last_run_successful: Optional[bool] = None
    last_run_message: Optional[str] = Field(None, max_length=255)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    paused: bool = False


class OrchestrationConfigurationStatusDetailResponse(
    BaseGetResponse, OrchestrationConfigurationStatusFields
):
    pass


class OrchestrationConfigurationStatusPostBody(
    BasePostBody, OrchestrationConfigurationStatusFields
):
    pass


class OrchestrationConfigurationStatusPatchBody(
    BasePatchBody, OrchestrationConfigurationStatusFields
):
    pass
