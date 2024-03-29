from ninja import Schema
from uuid import UUID
from typing import Optional
from sensorthings.validators import allow_partial
from core.schemas_old import BasePostBody, BasePatchBody


class ResultQualifierID(Schema):
    id: UUID


class ResultQualifierFields(Schema):
    code: str
    description: str


class ResultQualifierGetResponse(ResultQualifierFields, ResultQualifierID):
    owner: Optional[str]

    class Config:
        allow_population_by_field_name = True


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    pass


@allow_partial
class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
