from ninja import Schema, Field
from pydantic import ConfigDict, AliasChoices, AliasPath, StringConstraints as StrCon
from uuid import UUID
from typing import Optional, Annotated
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class ObservedPropertyID(Schema):
    id: UUID


class ObservedPropertyFields(Schema):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    definition: Annotated[str, StrCon(strip_whitespace=True)]
    description: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    type: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    code: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None


class ObservedPropertyGetResponse(BaseGetResponse, ObservedPropertyFields, ObservedPropertyID):
    model_config = ConfigDict(populate_by_name=True)

    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )


class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
    pass


class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
    pass
