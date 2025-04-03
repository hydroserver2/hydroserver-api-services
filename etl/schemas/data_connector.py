import uuid
from ninja import Schema, Field
from typing import Optional, Literal
from datetime import datetime
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from sta.schemas.datastream import DatastreamFields
from .orchestration_system import OrchestrationSystemGetResponse


class LinkedDatastreamFields(Schema):
    is_data_source: bool = False


class LinkedDatastreamGetResponse(BaseGetResponse, DatastreamFields):
    pass


class LinkedDatastreamPostBody(BasePostBody):
    datastream_id: uuid.UUID


class LinkedDatastreamPatchBody(BasePatchBody, LinkedDatastreamFields):
    pass


class DataConnectorScheduleFields(Schema):
    interval: Optional[int] = Field(None, gt=0)
    interval_units: Optional[Literal["minutes", "hours", "days"]] = None
    crontab: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DataConnectorScheduleGetResponse(BaseGetResponse, DataConnectorScheduleFields):
    pass


class DataConnectorSchedulePostBody(BasePatchBody, DataConnectorScheduleFields):
    pass


class DataConnectorSchedulePatchBody(BasePatchBody, DataConnectorScheduleFields):
    pass


class DataConnectorStatusFields(Schema):
    last_run_successful: Optional[bool] = None
    last_run_message: Optional[str] = Field(None, max_length=255)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    paused: bool = False


class DataConnectorStatusGetResponse(BaseGetResponse, DataConnectorStatusFields):
    pass


class DataConnectorStatusPostBody(BasePatchBody, DataConnectorStatusFields):
    pass


class DataConnectorStatusPatchBody(BasePatchBody, DataConnectorStatusFields):
    pass


class DataConnectorFields(Schema):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataConnectorGetResponse(BaseGetResponse, DataConnectorFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    orchestration_system: OrchestrationSystemGetResponse
    schedule: Optional[DataConnectorScheduleGetResponse] = None
    status: Optional[DataConnectorStatusGetResponse] = None
    linked_datastreams: list[LinkedDatastreamGetResponse]


class DataConnectorPostBody(BasePostBody, DataConnectorFields):
    workspace_id: uuid.UUID
    orchestration_system_id: uuid.UUID
    schedule: Optional[DataConnectorSchedulePostBody] = None
    status: Optional[DataConnectorStatusPostBody] = None
    linked_datastreams: list[LinkedDatastreamPostBody]


class DataConnectorPatchBody(BasePatchBody, DataConnectorFields):
    schedule: Optional[DataConnectorSchedulePatchBody] = None
    status: Optional[DataConnectorStatusPatchBody] = None
