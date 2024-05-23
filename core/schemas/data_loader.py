from ninja import Schema
from uuid import UUID
from sensorthings.validators import disable_required_field_validation
from core.schemas import BasePostBody, BasePatchBody


class DataLoaderID(Schema):
    id: UUID


class DataLoaderFields(Schema):
    name: str


class DataLoaderGetResponse(DataLoaderFields, DataLoaderID):

    @classmethod
    def serialize(cls, data_loader):  # Temporary until after Pydantic v2 update
        return {
            'id': data_loader.id,
            **{field: getattr(data_loader, field) for field in DataLoaderFields.model_fields.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class DataLoaderPostBody(BasePostBody, DataLoaderFields):
    pass


@disable_required_field_validation
class DataLoaderPatchBody(BasePatchBody, DataLoaderFields):
    pass
