from ninja import Schema
from uuid import UUID
from sensorthings.validators import allow_partial


class DataLoaderID(Schema):
    id: UUID


class DataLoaderFields(Schema):
    name: str


class DataLoaderGetResponse(DataLoaderFields, DataLoaderID):
    pass

    class Config:
        allow_population_by_field_name = True


class DataLoaderPostBody(DataLoaderFields):
    pass


@allow_partial
class DataLoaderPatchBody(DataLoaderFields):
    pass
