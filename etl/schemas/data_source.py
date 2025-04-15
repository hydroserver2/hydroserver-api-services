import uuid
from ninja import Schema, Field
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from sta.schemas import DatastreamGetResponse
from .orchestration_configuration import (
    OrchestrationConfigurationScheduleGetResponse,
    OrchestrationConfigurationSchedulePostBody,
    OrchestrationConfigurationSchedulePatchBody,
    OrchestrationConfigurationStatusGetResponse,
    OrchestrationConfigurationStatusPostBody,
    OrchestrationConfigurationStatusPatchBody,
)
from .orchestration_system import OrchestrationSystemGetResponse


class DataSourceFields(Schema):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataSourceGetResponse(BaseGetResponse, DataSourceFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    orchestration_system: OrchestrationSystemGetResponse
    schedule: Optional[OrchestrationConfigurationScheduleGetResponse] = None
    status: Optional[OrchestrationConfigurationStatusGetResponse] = None
    datastreams: list[DatastreamGetResponse]


class DataSourcePostBody(BasePostBody, DataSourceFields):
    workspace_id: uuid.UUID
    orchestration_system_id: uuid.UUID
    schedule: Optional[OrchestrationConfigurationSchedulePostBody] = None
    status: Optional[OrchestrationConfigurationStatusPostBody] = None
    datastream_ids: Optional[list[uuid.UUID]] = None


class DataSourcePatchBody(BasePatchBody, DataSourceFields):
    orchestration_system_id: Optional[uuid.UUID] = None
    schedule: Optional[OrchestrationConfigurationSchedulePatchBody] = None
    status: Optional[OrchestrationConfigurationStatusPatchBody] = None
