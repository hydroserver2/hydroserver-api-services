import uuid
from ninja import Schema, Field
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class EtlSystemPlatformFields(Schema):
    name: str = Field(..., max_length=255)
    interval_schedule_supported: bool
    crontab_schedule_supported: bool


class EtlSystemPlatformGetResponse(BaseGetResponse, EtlSystemPlatformFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class EtlSystemPlatformPostBody(BasePostBody, EtlSystemPlatformFields):
    workspace_id: uuid.UUID


class EtlSystemPlatformPatchBody(BasePatchBody, EtlSystemPlatformFields):
    pass
