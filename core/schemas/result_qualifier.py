from ninja import Schema, Field
from pydantic import AliasChoices, AliasPath
from uuid import UUID
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ResultQualifierID(Schema):
    id: UUID


class ResultQualifierFields(Schema):
    code: str
    description: str


class ResultQualifierGetResponse(BaseGetResponse, ResultQualifierFields, ResultQualifierID):
    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )

    class Config:
        allow_population_by_field_name = True


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    pass


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
