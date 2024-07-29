from ninja import Schema
from uuid import UUID
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class DataLoaderID(Schema):
    id: UUID


class DataLoaderFields(Schema):
    name: str


class DataLoaderGetResponse(BaseGetResponse, DataLoaderFields, DataLoaderID):

    class Config:
        allow_population_by_field_name = True


class DataLoaderPostBody(BasePostBody, DataLoaderFields):
    pass


class DataLoaderPatchBody(BasePatchBody, DataLoaderFields):
    pass
