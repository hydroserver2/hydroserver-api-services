import uuid
from ninja import Schema, Field
from typing import Optional, TYPE_CHECKING
from api.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from .orchestration_configuration import (
    OrchestrationConfigurationScheduleDetailResponse,
    OrchestrationConfigurationSchedulePostBody,
    OrchestrationConfigurationSchedulePatchBody,
    OrchestrationConfigurationStatusDetailResponse,
    OrchestrationConfigurationStatusPostBody,
    OrchestrationConfigurationStatusPatchBody,
)

if TYPE_CHECKING:
    # from iam.schemas import WorkspaceSummaryResponse
    from etl.schemas import OrchestrationSystemSummaryResponse
    from sta.schemas import DatastreamSummaryResponse


class DataSourceFields(Schema):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataSourceSummaryResponse(BaseGetResponse, DataSourceFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    orchestration_system_id: uuid.UUID
    schedule: Optional[OrchestrationConfigurationScheduleDetailResponse] = None
    status: Optional[OrchestrationConfigurationStatusDetailResponse] = None


class DataSourceDetailResponse(BaseGetResponse, DataSourceFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    # workspace: "WorkspaceSummaryResponse"
    orchestration_system: "OrchestrationSystemSummaryResponse"
    schedule: Optional[OrchestrationConfigurationScheduleDetailResponse] = None
    status: Optional[OrchestrationConfigurationStatusDetailResponse] = None
    datastreams: Optional[list["DatastreamSummaryResponse"]] = None


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
