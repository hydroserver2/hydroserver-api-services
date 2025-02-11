import uuid
from ninja import Schema, Field
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ResultQualifierFields(Schema):
    code: str = Field(..., max_length=255)
    description: str


class ResultQualifierGetResponse(BaseGetResponse, ResultQualifierFields):
    id: uuid.UUID
    workspace_id: uuid.UUID


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    workspace_id: uuid.UUID


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
