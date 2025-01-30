from ninja import Schema
from pydantic import ConfigDict, Field, AliasChoices, AliasPath, StringConstraints as StrCon
from uuid import UUID
from typing import Optional, Annotated
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class SensorID(Schema):
    id: UUID


class SensorFields(Schema):
    name: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]]
    description: Annotated[str, StrCon(strip_whitespace=True)]
    encoding_type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    manufacturer: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    model: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    model_link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=500)]] = None
    method_type: Annotated[str, StrCon(strip_whitespace=True, max_length=100)]
    method_link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=500)]] = None
    method_code: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=50)]] = None


class SensorGetResponse(BaseGetResponse, SensorFields, SensorID):
    model_config = ConfigDict(populate_by_name=True)

    owner: Optional[str] = Field(
        None, serialization_alias='owner',
        validation_alias=AliasChoices('owner', AliasPath('person', 'email'))
    )


class SensorPostBody(BasePostBody, SensorFields):
    pass


class SensorPatchBody(BasePatchBody, SensorFields):
    pass
