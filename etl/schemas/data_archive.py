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
    from iam.schemas import WorkspaceSummaryResponse
    from etl.schemas import OrchestrationSystemSummaryResponse
    from sta.schemas import DatastreamSummaryResponse


class DataArchiveFields(Schema):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataArchiveSummaryResponse(BaseGetResponse, DataArchiveFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    orchestration_system_id: uuid.UUID
    schedule: Optional[OrchestrationConfigurationScheduleDetailResponse] = None
    status: Optional[OrchestrationConfigurationStatusDetailResponse] = None


class DataArchiveDetailResponse(BaseGetResponse, DataArchiveFields):
    id: uuid.UUID
    workspace: "WorkspaceSummaryResponse"
    orchestration_system: "OrchestrationSystemSummaryResponse"
    schedule: Optional[OrchestrationConfigurationScheduleDetailResponse] = None
    status: Optional[OrchestrationConfigurationStatusDetailResponse] = None
    datastreams: Optional[list["DatastreamSummaryResponse"]] = None


class DataArchivePostBody(BasePostBody, DataArchiveFields):
    workspace_id: uuid.UUID
    orchestration_system_id: uuid.UUID
    schedule: Optional[OrchestrationConfigurationSchedulePostBody] = None
    status: Optional[OrchestrationConfigurationStatusPostBody] = None
    datastream_ids: Optional[list[uuid.UUID]] = None


class DataArchivePatchBody(BasePatchBody, DataArchiveFields):
    orchestration_system_id: Optional[uuid.UUID] = None
    schedule: Optional[OrchestrationConfigurationSchedulePatchBody] = None
    status: Optional[OrchestrationConfigurationStatusPatchBody] = None
