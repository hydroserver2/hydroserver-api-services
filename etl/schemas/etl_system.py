import uuid
from ninja import Schema, Field
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from .etl_system_platform import EtlSystemPlatformGetResponse


class EtlSystemFields(Schema):
    name: str = Field(..., max_length=255)


class EtlSystemGetResponse(BaseGetResponse, EtlSystemFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]
    etl_system_platform: EtlSystemPlatformGetResponse


class EtlSystemPostBody(BasePostBody, EtlSystemFields):
    workspace_id: uuid.UUID
    etl_system_platform_id: uuid.UUID


class EtlSystemPatchBody(BasePatchBody, EtlSystemFields):
    pass
