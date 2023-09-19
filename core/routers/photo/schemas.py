from ninja import Schema
from pydantic import Field
from typing import List, Optional
from uuid import UUID


class PhotoID(Schema):
    id: UUID


class PhotoFields(Schema):
    thing_id: UUID = Field(..., alias='thingId')
    file_path: str = Field(..., alias='filePath')
    link: str


class PhotoGetResponse(PhotoFields, PhotoID):
    pass

    class Config:
        allow_population_by_field_name = True


class PhotoPostBody(Schema):
    photos_to_delete: Optional[List[UUID]] = []
