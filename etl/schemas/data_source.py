import uuid
from ninja import Schema, Field
from typing import Optional, TYPE_CHECKING
from api.schemas import BaseDetailResponse, BasePostBody, BasePatchBody
from .orchestration_configuration import (
    OrchestrationConfigurationScheduleDetailResponse,
    OrchestrationConfigurationSchedulePostBody,
    OrchestrationConfigurationSchedulePatchBody,
    OrchestrationConfigurationStatusDetailResponse,
    OrchestrationConfigurationStatusPostBody,
    OrchestrationConfigurationStatusPatchBody,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceDetailResponse
    from etl.schemas import OrchestrationSystemDetailResponse


class DataSourceFields(Schema):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataSourceSummaryResponse(BaseDetailResponse, DataSourceFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    orchestration_system_id: uuid.UUID
    schedule: Optional[OrchestrationConfigurationScheduleDetailResponse] = None
    status: Optional[OrchestrationConfigurationStatusDetailResponse] = None


class DataSourceDetailResponse(BaseDetailResponse, DataSourceFields):
    id: uuid.UUID
    workspace: "WorkspaceDetailResponse"
    orchestration_system: "OrchestrationSystemDetailResponse"
    schedule: Optional[OrchestrationConfigurationScheduleDetailResponse] = None
    status: Optional[OrchestrationConfigurationStatusDetailResponse] = None


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
