# from ninja import Schema
# from uuid import UUID
# from typing import Optional
# from sensorthings.validators import allow_partial
# from core.schemas_old import BasePostBody, BasePatchBody
#
#
# class ProcessingLevelID(Schema):
#     id: UUID
#
#
# class ProcessingLevelFields(Schema):
#     code: str
#     definition: str = None
#     explanation: str = None
#
#
# class ProcessingLevelGetResponse(ProcessingLevelFields, ProcessingLevelID):
#     owner: Optional[str]
#
#     class Config:
#         allow_population_by_field_name = True
#
#
# class ProcessingLevelPostBody(BasePostBody, ProcessingLevelFields):
#     pass
#
#
# @allow_partial
# class ProcessingLevelPatchBody(BasePatchBody, ProcessingLevelFields):
#     pass
