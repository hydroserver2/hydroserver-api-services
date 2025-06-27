import uuid
from ninja import Schema, Field, Query
from typing import Optional, Literal
from pydantic import AliasChoices
from datetime import datetime
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class DatastreamFields(Schema):
    name: str = Field(..., max_length=255)
    description: str
    observation_type: str = Field(..., max_length=255)
    sampled_medium: str = Field(..., max_length=255)
    no_data_value: float
    aggregation_statistic: str = Field(..., max_length=255)
    time_aggregation_interval: float
    status: Optional[str] = Field(None, max_length=255)
    result_type: str = Field(..., max_length=255)
    value_count: Optional[int] = Field(None, ge=0)
    phenomenon_begin_time: Optional[datetime] = None
    phenomenon_end_time: Optional[datetime] = None
    result_begin_time: Optional[datetime] = None
    result_end_time: Optional[datetime] = None
    is_private: bool = False
    is_visible: bool = True
    thing_id: uuid.UUID
    sensor_id: uuid.UUID
    observed_property_id: uuid.UUID
    processing_level_id: uuid.UUID
    unit_id: uuid.UUID
    time_aggregation_interval_unit: Literal["seconds", "minutes", "hours", "days"]
    intended_time_spacing: Optional[float] = None
    intended_time_spacing_unit: Optional[
        Literal["seconds", "minutes", "hours", "days"]
    ] = None


class DatastreamQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter datastreams by workspace ID."
    )
    thing_id: list[uuid.UUID] = Query([], description="Filter datastreams by thing ID.")
    sensor_id: list[uuid.UUID] = Query(
        [], description="Filter datastreams by sensor ID."
    )
    observed_property_id: list[uuid.UUID] = Query(
        [], description="Filter datastreams by observed property ID."
    )
    processing_level_id: list[uuid.UUID] = Query(
        [], description="Filter datastreams by processing level ID."
    )
    unit_id: list[uuid.UUID] = Query([], description="Filter datastreams by unit ID.")
    observation_type: list[str] = Query(
        [], description="Filter things by observation type."
    )
    sampled_medium: list[str] = Query(
        [], description="Filter things by sampled medium."
    )
    status: list[str] = Query([], description="Filter things by status.")
    result_type: list[str] = Query([], description="Filter things by result type.")
    is_private: Optional[bool] = Query(
        None,
        description="Controls whether the datastreams should be private or public.",
    )
    value_count__lte: Optional[int] = Query(
        None,
        description="Sets the maximum value count of filtered datastreams.",
        alias="value_count_max",
    )
    value_count__gte: Optional[int] = Query(
        None,
        description="Sets the minimum value count of filtered datastreams.",
        alias="value_count_min",
    )
    phenomenon_begin_time__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum phenomenon begin time of filtered datastreams.",
        alias="phenomenon_begin_time_max",
    )
    phenomenon_begin_time__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum phenomenon begin time of filtered datastreams.",
        alias="phenomenon_begin_time_min",
    )
    phenomenon_end_time__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum phenomenon end time of filtered datastreams.",
        alias="phenomenon_end_time_max",
    )
    phenomenon_end_time__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum phenomenon end time of filtered datastreams.",
        alias="phenomenon_end_time_min",
    )
    result_begin_time__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum result begin time of filtered datastreams.",
        alias="result_begin_time_max",
    )
    result_begin_time__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum result begin time of filtered datastreams.",
        alias="result_begin_time_min",
    )
    result_end_time__lte: Optional[datetime] = Query(
        None,
        description="Sets the maximum result end time of filtered datastreams.",
        alias="result_end_time_max",
    )
    result_end_time__gte: Optional[datetime] = Query(
        None,
        description="Sets the minimum result end time of filtered datastreams.",
        alias="result_end_time_min",
    )


class DatastreamGetResponse(BaseGetResponse, DatastreamFields):
    id: uuid.UUID
    data_source_id: Optional[uuid.UUID] = None
    workspace_id: Optional[uuid.UUID] = Field(
        None, validation_alias=AliasChoices("workspaceId", "thing.workspace_id")
    )


class DatastreamPostBody(BasePostBody, DatastreamFields):
    pass


class DatastreamPatchBody(BasePatchBody, DatastreamFields):
    pass


class ObservationsGetResponse(BaseGetResponse):
    phenomenon_time: list
    result: list
