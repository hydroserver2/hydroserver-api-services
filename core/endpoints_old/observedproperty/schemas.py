# from ninja import Schema
# from uuid import UUID
# from typing import Optional
# from sensorthings.validators import allow_partial
# from core.schemas_old import BasePostBody, BasePatchBody
#
#
# class ObservedPropertyID(Schema):
#     id: UUID
#
#
# class ObservedPropertyFields(Schema):
#     name: str
#     definition: str
#     description: str = None
#     type: str = None
#     code: str = None
#
#
# class ObservedPropertyGetResponse(ObservedPropertyFields, ObservedPropertyID):
#     owner: Optional[str]
#
#     class Config:
#         allow_population_by_field_name = True
#
#
# class ObservedPropertyPostBody(BasePostBody, ObservedPropertyFields):
#     pass
#
#
# @allow_partial
# class ObservedPropertyPatchBody(BasePatchBody, ObservedPropertyFields):
#     pass
