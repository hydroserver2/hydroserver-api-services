# from ninja import Path
# from uuid import UUID
# from django.db import transaction, IntegrityError
# from core.router import DataManagementRouter
# from core.models import DataLoader
# from core.endpoints.datasource.schemas import DataSourceGetResponse
# from core.endpoints.datasource.utils import query_data_sources, build_data_source_response
# from .schemas import DataLoaderGetResponse, DataLoaderPostBody, DataLoaderPatchBody, \
#     DataLoaderFields
# from .utils import query_data_loaders, get_data_loader_by_id, build_data_loader_response, check_data_loader_by_id
#
#
# router = DataManagementRouter(tags=['Data Loaders'])
#
#
# @router.dm_list('', response=DataLoaderGetResponse)
# def get_data_loaders(request):
#     """
#     Get a list of Data Loaders
#
#     This endpoint returns a list of Data Loaders owned by the authenticated user.
#     """
#
#     data_loader_query, _ = query_data_loaders(
#         user=getattr(request, 'authenticated_user', None),
#         require_ownership=True
#     )
#
#     return [
#         build_data_loader_response(data_loader) for data_loader in data_loader_query.all()
#     ]
#
#
# @router.dm_get('{data_loader_id}', response=DataLoaderGetResponse)
# def get_data_loader(request, data_loader_id: UUID = Path(...)):
#     """
#     Get details for a Data Loader
#
#     This endpoint returns details for a Data Loader given a Data Loader ID.
#     """
#
#     data_loader = get_data_loader_by_id(
#         user=request.authenticated_user,
#         data_loader_id=data_loader_id,
#         raise_http_errors=True
#     )
#
#     return 200, build_data_loader_response(data_loader)
#
#
# @router.dm_post('', response=DataLoaderGetResponse)
# @transaction.atomic
# def create_data_loader(request, data: DataLoaderPostBody):
#     """
#     Create a Data Loader
#
#     This endpoint will create a new Data Loader owned by the authenticated user and returns the created Processing
#     Level.
#     """
#
#     data_loader = DataLoader.objects.create(
#         person=request.authenticated_user,
#         **data.dict(include=set(DataLoaderFields.__fields__.keys()))
#     )
#
#     data_loader = get_data_loader_by_id(
#         user=request.authenticated_user,
#         data_loader_id=data_loader.id,
#         raise_http_errors=True
#     )
#
#     return 201, build_data_loader_response(data_loader)
#
#
# @router.dm_patch('{data_loader_id}', response=DataLoaderGetResponse)
# @transaction.atomic
# def update_data_loader(request, data: DataLoaderPatchBody, data_loader_id: UUID = Path(...)):
#     """
#     Update a Data Loader
#
#     This endpoint will update an existing Data Loader owned by the authenticated user and return the updated
#     Data Loader.
#     """
#
#     data_loader = get_data_loader_by_id(
#         user=request.authenticated_user,
#         data_loader_id=data_loader_id,
#         require_ownership=True,
#         raise_http_errors=True
#     )
#
#     data_loader_data = data.dict(include=set(DataLoaderFields.__fields__.keys()), exclude_unset=True)
#
#     for field, value in data_loader_data.items():
#         setattr(data_loader, field, value)
#
#     data_loader.save()
#
#     data_loader = get_data_loader_by_id(
#         user=request.authenticated_user,
#         data_loader_id=data_loader_id
#     )
#
#     return 203, build_data_loader_response(data_loader)
#
#
# @router.dm_delete('{data_loader_id}')
# @transaction.atomic
# def delete_data_loader(request, data_loader_id: UUID = Path(...)):
#     """
#     Delete a Data Loader
#
#     This endpoint will delete an existing Data Loader if the authenticated user is the primary owner of the
#     Data Loader.
#     """
#
#     data_loader = get_data_loader_by_id(
#         user=request.authenticated_user,
#         data_loader_id=data_loader_id,
#         require_ownership=True,
#         raise_http_errors=True
#     )
#
#     try:
#         data_loader.delete()
#     except IntegrityError as e:
#         return 409, str(e)
#
#     return 204, None
#
#
# @router.dm_list(
#     '{data_loader_id}/data-sources',
#     response=DataSourceGetResponse
# )
# def get_dataloader_data_sources(request, data_loader_id: UUID = Path(...)):
#     """
#     Get a list of Data Source for a Data Loader
#
#     This endpoint returns a list of Data Sources owned by the authenticated user if there is one
#     associated with the given Data Loader ID.
#     """
#
#     check_data_loader_by_id(
#         user=request.authenticated_user,
#         data_loader_id=data_loader_id,
#         raise_http_errors=True
#     )
#
#     data_source_query, _ = query_data_sources(
#         user=request.authenticated_user,
#         data_loader_ids=[data_loader_id]
#     )
#
#     return [
#         build_data_source_response(data_source) for data_source in data_source_query.all()
#     ]
