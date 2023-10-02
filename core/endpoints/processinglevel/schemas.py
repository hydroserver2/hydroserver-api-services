from ninja import Schema
from uuid import UUID
from typing import Optional
from sensorthings.validators import allow_partial
from accounts.schemas import UserFields


class ProcessingLevelID(Schema):
    id: UUID


class ProcessingLevelFields(Schema):
    code: str
    definition: str = None
    explanation: str = None


class ProcessingLevelGetResponse(ProcessingLevelFields, ProcessingLevelID):
    owner: Optional[UserFields]

    class Config:
        allow_population_by_field_name = True


class ProcessingLevelPostBody(ProcessingLevelFields):
    pass


@allow_partial
class ProcessingLevelPatchBody(ProcessingLevelFields):
    pass
