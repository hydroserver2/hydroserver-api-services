import uuid
from typing import Optional
from ninja import Schema, Field, Query
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class ProcessingLevelFields(Schema):
    code: str = Field(..., max_length=255)
    definition: Optional[str] = None
    explanation: Optional[str] = None


class ProcessingLevelQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter processing levels by workspace ID."
    )
    thing_id: list[uuid.UUID] = Query(
        [], description="Filter processing levels by thing ID."
    )
    datastream_id: list[uuid.UUID] = Query(
        [], description="Filter processing levels by datastream ID."
    )
    code: list[str] = Query([], description="Filter processing levels by code")


class ProcessingLevelGetResponse(BaseGetResponse, ProcessingLevelFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class ProcessingLevelPostBody(BasePostBody, ProcessingLevelFields):
    workspace_id: uuid.UUID


class ProcessingLevelPatchBody(BasePatchBody, ProcessingLevelFields):
    pass
