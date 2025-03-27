import uuid
from ninja import Schema, Field
from typing import Optional, Literal
from pydantic import AliasChoices
from datetime import datetime
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


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


class DatastreamGetResponse(BaseGetResponse, DatastreamFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = Field(
        None, validation_alias=AliasChoices("workspaceId", "thing.workspace_id")
    )


class DatastreamPostBody(BasePostBody, DatastreamFields):
    pass


class DatastreamPatchBody(BasePatchBody, DatastreamFields):
    pass
