import uuid
from typing import Optional
from ninja import Schema, Field
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ProcessingLevelFields(Schema):
    code: str = Field(..., max_length=255)
    definition: Optional[str] = None
    explanation: Optional[str] = None


class ProcessingLevelGetResponse(BaseGetResponse, ProcessingLevelFields):
    id: uuid.UUID
    workspace_id: uuid.UUID


class ProcessingLevelPostBody(BasePostBody, ProcessingLevelFields):
    workspace_id: uuid.UUID


class ProcessingLevelPatchBody(BasePatchBody, ProcessingLevelFields):
    pass
