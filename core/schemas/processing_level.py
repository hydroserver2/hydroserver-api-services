from ninja import Schema
from uuid import UUID
from typing import Optional
from sensorthings.validators import disable_required_field_validation
from core.schemas import BasePostBody, BasePatchBody


class ProcessingLevelID(Schema):
    id: UUID


class ProcessingLevelFields(Schema):
    code: str
    definition: str = None
    explanation: str = None


class ProcessingLevelGetResponse(ProcessingLevelFields, ProcessingLevelID):
    owner: Optional[str]

    @classmethod
    def serialize(cls, processing_level):  # Temporary until after Pydantic v2 update
        return {
            'id': processing_level.id,
            'owner': processing_level.person.email if processing_level.person else None,
            **{field: getattr(processing_level, field) for field in ProcessingLevelFields.model_fields.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class ProcessingLevelPostBody(BasePostBody, ProcessingLevelFields):
    pass


@disable_required_field_validation
class ProcessingLevelPatchBody(BasePatchBody, ProcessingLevelFields):
    pass
