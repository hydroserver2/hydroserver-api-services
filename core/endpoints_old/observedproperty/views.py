# from ninja import Path
# from uuid import UUID
# from typing import Optional
# from django.db import transaction, IntegrityError
# from core.router import DataManagementRouter
# from core.models import ObservedProperty
# from core.schemas_old import metadataOwnerOptions
# from .schemas import ObservedPropertyGetResponse, ObservedPropertyPostBody, ObservedPropertyPatchBody, \
#     ObservedPropertyFields
# from .utils import query_observed_properties, get_observed_property_by_id, build_observed_property_response
#
#
# router = DataManagementRouter(tags=['Observed Properties'])
#
#
# @router.dm_list('', response=ObservedPropertyGetResponse)
# def get_observed_properties(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
#     """
#     Get a list of Observed Properties
#
#     This endpoint returns a list of Observed Properties owned by the authenticated user.
#     """
#
#     observed_property_query, _ = query_observed_properties(
#         user=getattr(request, 'authenticated_user', None),
#         require_ownership=True if owner == 'currentUser' else False,
#         require_ownership_or_unowned=True if owner == 'currentUserOrNoUser' else False,
#         raise_http_errors=False
#     )
#
#     return [
#         build_observed_property_response(observed_property) for observed_property in observed_property_query.all()
#         if owner in ['currentUser', 'currentUserOrNoUser', 'anyUserOrNoUser']
#         or (owner == 'noUser' and observed_property.person is None)
#         or (owner == 'anyUser' and observed_property.person is not None)
#     ]
#
#
# @router.dm_get('{observed_property_id}', response=ObservedPropertyGetResponse)
# def get_observed_property(request, observed_property_id: UUID = Path(...)):
#     """
#     Get details for an Observed Property
#
#     This endpoint returns details for an Observed Property given an Observed Property ID.
#     """
#
#     observed_property = get_observed_property_by_id(
#         user=request.authenticated_user,
#         observed_property_id=observed_property_id,
#         raise_http_errors=True
#     )
#
#     return 200, build_observed_property_response(observed_property)
#
#
# @router.dm_post('', response=ObservedPropertyGetResponse)
# @transaction.atomic
# def create_observed_property(request, data: ObservedPropertyPostBody):
#     """
#     Create an Observed Property
#
#     This endpoint will create a new Observed Property owned by the authenticated user and returns the created Observed
#     Property.
#     """
#
#     observed_property = ObservedProperty.objects.create(
#         person=request.authenticated_user,
#         **data.dict(include=set(ObservedPropertyFields.__fields__.keys()))
#     )
#
#     observed_property = get_observed_property_by_id(
#         user=request.authenticated_user,
#         observed_property_id=observed_property.id,
#         raise_http_errors=True
#     )
#
#     return 201, build_observed_property_response(observed_property)
#
#
# @router.dm_patch('{observed_property_id}', response=ObservedPropertyGetResponse)
# @transaction.atomic
# def update_observed_property(request, data: ObservedPropertyPatchBody, observed_property_id: UUID = Path(...)):
#     """
#     Update an Observed Property
#
#     This endpoint will update an existing ObservedProperty owned by the authenticated user and return the updated
#     Observed Property.
#     """
#
#     observed_property = get_observed_property_by_id(
#         user=request.authenticated_user,
#         observed_property_id=observed_property_id,
#         require_ownership=True,
#         raise_http_errors=True
#     )
#
#     observed_property_data = data.dict(include=set(ObservedPropertyFields.__fields__.keys()), exclude_unset=True)
#
#     for field, value in observed_property_data.items():
#         setattr(observed_property, field, value)
#
#     observed_property.save()
#
#     observed_property = get_observed_property_by_id(
#         user=request.authenticated_user,
#         observed_property_id=observed_property_id
#     )
#
#     return 203, build_observed_property_response(observed_property)
#
#
# @router.dm_delete('{observed_property_id}')
# @transaction.atomic
# def delete_observed_property(request, observed_property_id: UUID = Path(...)):
#     """
#     Delete an Observed Property
#
#     This endpoint will delete an existing ObservedProperty if the authenticated user is the primary owner of the
#     Observed Property.
#     """
#
#     observed_property = get_observed_property_by_id(
#         user=request.authenticated_user,
#         observed_property_id=observed_property_id,
#         require_ownership=True,
#         raise_http_errors=True
#     )
#
#     try:
#         observed_property.delete()
#     except IntegrityError as e:
#         return 409, str(e)
#
#     return 204, None
