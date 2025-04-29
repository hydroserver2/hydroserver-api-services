import uuid
from ninja import Schema, Field
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class OrchestrationSystemFields(Schema):
    name: str = Field(..., max_length=255)
    orchestration_system_type: str = Field(..., max_length=255, alias="type")


class OrchestrationSystemGetResponse(BaseGetResponse, OrchestrationSystemFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class OrchestrationSystemPostBody(BasePostBody, OrchestrationSystemFields):
    workspace_id: uuid.UUID


class OrchestrationSystemPatchBody(BasePatchBody, OrchestrationSystemFields):
    pass
