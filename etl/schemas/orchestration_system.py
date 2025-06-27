import uuid
from ninja import Schema, Field, Query
from typing import Optional
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class OrchestrationSystemFields(Schema):
    name: str = Field(..., max_length=255)
    orchestration_system_type: str = Field(..., max_length=255, alias="type")


class OrchestrationSystemQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by workspace ID."
    )
    orchestration_system_type: list[str] = Query(
        [], description="Filter orchestration systems by type.", alias="type"
    )


class OrchestrationSystemGetResponse(BaseGetResponse, OrchestrationSystemFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class OrchestrationSystemPostBody(BasePostBody, OrchestrationSystemFields):
    workspace_id: uuid.UUID


class OrchestrationSystemPatchBody(BasePatchBody, OrchestrationSystemFields):
    pass
