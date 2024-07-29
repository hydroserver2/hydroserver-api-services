from ninja import Schema, Field
from pydantic import AliasChoices, AliasPath
from uuid import UUID
from typing import Optional
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ProcessingLevelID(Schema):
    id: UUID


class ProcessingLevelFields(Schema):
    code: str
    definition: Optional[str] = None
    explanation: Optional[str] = None


class ProcessingLevelGetResponse(BaseGetResponse, ProcessingLevelFields, ProcessingLevelID):
    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )

    class Config:
        allow_population_by_field_name = True


class ProcessingLevelPostBody(BasePostBody, ProcessingLevelFields):
    pass


class ProcessingLevelPatchBody(BasePatchBody, ProcessingLevelFields):
    pass
