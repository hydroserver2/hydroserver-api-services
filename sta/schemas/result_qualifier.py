import uuid
from typing import Optional
from ninja import Schema, Field, Query
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)


class ResultQualifierFields(Schema):
    code: str = Field(..., max_length=255)
    description: str


class ResultQualifierQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by workspace ID."
    )
    code: list[str] = Query([], description="Filter result qualifiers by code")


class ResultQualifierGetResponse(BaseGetResponse, ResultQualifierFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID]


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    workspace_id: uuid.UUID


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
