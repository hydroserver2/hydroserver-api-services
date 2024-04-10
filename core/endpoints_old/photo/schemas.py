# from ninja import Schema
# from pydantic import Field
# from uuid import UUID
#
#
# class PhotoID(Schema):
#     id: UUID
#
#
# class PhotoFields(Schema):
#     thing_id: UUID = Field(..., alias='thingId')
#     file_path: str = Field(..., alias='filePath')
#     link: str
#
#
# class PhotoGetResponse(PhotoFields, PhotoID):
#     pass
#
#     class Config:
#         allow_population_by_field_name = True
