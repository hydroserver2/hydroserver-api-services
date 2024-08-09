from ninja import Schema
from typing import Annotated
from pydantic import StringConstraints as StrCon
from uuid import UUID
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class DataLoaderID(Schema):
    id: UUID


class DataLoaderFields(Schema):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]


class DataLoaderGetResponse(BaseGetResponse, DataLoaderFields, DataLoaderID):

    class Config:
        allow_population_by_field_name = True


class DataLoaderPostBody(BasePostBody, DataLoaderFields):
    pass


class DataLoaderPatchBody(BasePatchBody, DataLoaderFields):
    pass
