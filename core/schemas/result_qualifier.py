from ninja import Schema
from uuid import UUID
from typing import Optional
from core.schemas import BasePostBody, BasePatchBody


class ResultQualifierID(Schema):
    id: UUID


class ResultQualifierFields(Schema):
    code: str
    description: str


class ResultQualifierGetResponse(ResultQualifierFields, ResultQualifierID):
    owner: Optional[str]

    @classmethod
    def serialize(cls, result_qualifier):  # Temporary until after Pydantic v2 update
        return {
            'id': result_qualifier.id,
            'owner': result_qualifier.person.email if result_qualifier.person else None,
            **{field: getattr(result_qualifier, field) for field in ResultQualifierFields.model_fields.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class ResultQualifierPostBody(BasePostBody, ResultQualifierFields):
    pass


class ResultQualifierPatchBody(BasePatchBody, ResultQualifierFields):
    pass
