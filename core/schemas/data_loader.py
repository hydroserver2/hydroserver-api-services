from ninja import Schema
from typing import Annotated
from pydantic import ConfigDict, StringConstraints as StrCon
from uuid import UUID
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class DataLoaderID(Schema):
    id: UUID


class DataLoaderFields(Schema):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]


class DataLoaderGetResponse(BaseGetResponse, DataLoaderFields, DataLoaderID):
    model_config = ConfigDict(populate_by_name=True)


class DataLoaderPostBody(BasePostBody, DataLoaderFields):
    pass


class DataLoaderPatchBody(BasePatchBody, DataLoaderFields):
    pass
