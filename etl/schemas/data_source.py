import uuid
from ninja import Schema, Field
from typing import Optional, Literal
from datetime import datetime
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class LinkedDatastreamProperties(BaseGetResponse, Schema):
    name: str = Field(..., max_length=255)
    description: str
    no_data_value: float
    value_count: Optional[int] = Field(None, ge=0)
    phenomenon_begin_time: Optional[datetime] = None
    phenomenon_end_time: Optional[datetime] = None
    result_begin_time: Optional[datetime] = None
    result_end_time: Optional[datetime] = None
    aggregation_statistic: str = Field(..., max_length=255)
    time_aggregation_interval: float
    time_aggregation_interval_unit: Literal["seconds", "minutes", "hours", "days"]
    intended_time_spacing: Optional[float] = None
    intended_time_spacing_unit: Optional[
        Literal["seconds", "minutes", "hours", "days"]
    ] = None


class LinkedDatastreamFields(Schema):
    extractor_configuration_id: Optional[uuid.UUID] = None
    extractor_configuration_settings: Optional[dict] = None
    transformer_configuration_id: Optional[uuid.UUID] = None
    transformer_configuration_settings: Optional[dict] = None
    loader_configuration_id: Optional[uuid.UUID] = None
    loader_configuration_settings: Optional[dict] = None


class LinkedDatastreamGetResponse(BaseGetResponse, LinkedDatastreamFields):
    datastream: LinkedDatastreamProperties


class LinkedDatastreamPostBody(BasePostBody, LinkedDatastreamFields):
    pass


class LinkedDatastreamPatchBody(BasePatchBody, LinkedDatastreamFields):
    pass


class DataSourceFields(Schema):
    name: str = Field(..., max_length=255)
    etl_system_id: uuid.UUID
    interval: Optional[int] = Field(None, gt=0)
    interval_units: Optional[Literal["minutes", "hours", "days"]] = None
    crontab: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    paused: bool = False
    last_run_successful: Optional[bool] = None
    last_run_message: Optional[str] = Field(None, max_length=255)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    extractor_configuration_id: Optional[uuid.UUID] = None
    extractor_configuration_settings: Optional[dict] = None
    transformer_configuration_id: Optional[uuid.UUID] = None
    transformer_configuration_settings: Optional[dict] = None
    loader_configuration_id: Optional[uuid.UUID] = None
    loader_configuration_settings: Optional[dict] = None


class DataSourceGetResponse(BaseGetResponse, DataSourceFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    linked_datastreams: list[LinkedDatastreamGetResponse]


class DataSourcePostBody(BasePostBody, DataSourceFields):
    workspace_id: uuid.UUID


class DataSourcePatchBody(BasePatchBody, DataSourceFields):
    pass
