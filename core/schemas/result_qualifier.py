from ninja import Schema, Field
from pydantic import ConfigDict, AliasChoices, AliasPath, StringConstraints as StrCon
from uuid import UUID
from typing import Optional, Annotated
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ResultQualifierID(Schema):
    id: UUID


class ResultQualifierFields(Schema):
    code: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]]
    description: Optional[Annotated[str, StrCon(strip_whitespace=True)]]


class ResultQualifierGetResponse(BaseGetResponse, ResultQualifierFields, ResultQualifierID):
    model_config = ConfigDict(populate_by_name=True)

    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    pass


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
