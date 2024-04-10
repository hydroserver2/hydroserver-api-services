# from uuid import UUID
# from ninja import Schema
# from sensorthings.validators import allow_partial
#
#
# class TagID(Schema):
#     id: UUID
#
#
# class TagFields(Schema):
#     key: str
#     value: str
#
#
# class TagGetResponse(TagFields, TagID):
#     pass
#
#     class Config:
#         allow_population_by_field_name = True
#
#
# class TagPostBody(TagFields):
#     pass
#
#
# @allow_partial
# class TagPatchBody(TagFields):
#     pass
