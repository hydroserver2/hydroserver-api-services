from ninja import Path
from uuid import UUID
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import DataLoader, DataSource
from core.schemas.data_loader import DataLoaderGetResponse, DataLoaderPostBody, DataLoaderPatchBody, \
    DataLoaderFields
from core.schemas.data_source import DataSourceGetResponse


router = DataManagementRouter(tags=['Data Loaders'])


@router.dm_list('', response=DataLoaderGetResponse)
def get_data_loaders(request):
    """
    Get a list of Data Loaders

    This endpoint returns a list of data loaders owned by the authenticated user.
    """

    data_loader_query = DataLoader.objects.select_related('person')
    data_loader_query = data_loader_query.filter(person__is_active=True)
    data_loader_query = data_loader_query.filter(Q(person=request.authenticated_user))
    data_loader_query = data_loader_query.apply_permissions(request.authenticated_user, 'GET')

    data_loader_query = data_loader_query.distinct()

    response = [data_loader for data_loader in data_loader_query.all()]

    return 200, response


@router.dm_get('{data_loader_id}', response=DataLoaderGetResponse)
def get_data_loader(request, data_loader_id: UUID = Path(...)):
    """
    Get details for a Data Loader

    This endpoint returns details for a data loader given a data loader ID.
    """

    data_loader = DataLoader.objects.get_by_id(
        data_loader_id=data_loader_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, data_loader


@router.dm_post('', response=DataLoaderGetResponse)
@transaction.atomic
def create_data_loader(request, data: DataLoaderPostBody):
    """
    Create a Data Loader

    This endpoint will create a new data loader owned by the authenticated user and returns the created data loader.
    """

    data_loader = DataLoader.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(DataLoaderFields.model_fields.keys()))
    )

    return 201, data_loader


@router.dm_patch('{data_loader_id}', response=DataLoaderGetResponse)
@transaction.atomic
def update_data_loader(request, data: DataLoaderPatchBody, data_loader_id: UUID = Path(...)):
    """
    Update a Data Loader

    This endpoint will update an existing data loader owned by the authenticated user and return the updated
    data loader.
    """

    data_loader = DataLoader.objects.get_by_id(
        data_loader_id=data_loader_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    data_loader_data = data.dict(include=set(DataLoaderFields.model_fields.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'DataLoader', fields=[*data_loader_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this data loader.'

    for field, value in data_loader_data.items():
        setattr(data_loader, field, value)

    data_loader.save()

    return 203, data_loader


@router.dm_delete('{data_loader_id}')
@transaction.atomic
def delete_data_loader(request, data_loader_id: UUID = Path(...)):
    """
    Delete a Data Loader

    This endpoint will delete an existing Data Loader if the authenticated user is the primary owner of the
    data loader.
    """

    data_loader = DataLoader.objects.get_by_id(
        data_loader_id=data_loader_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        data_loader.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None


@router.dm_list(
    '{data_loader_id}/data-sources',
    response=DataSourceGetResponse
)
def get_data_loader_data_sources(request, data_loader_id: UUID = Path(...)):
    """
    Get a list of Data Source for a Data Loader

    This endpoint returns a list of data sources owned by the authenticated user if there is one
    associated with the given data loader ID.
    """

    DataLoader.objects.get_by_id(
        data_loader_id=data_loader_id,
        user=request.authenticated_user,
        method='GET',
        model='DataSource',
        raise_404=True,
        fetch=False
    )

    data_source_query = DataSource.objects.select_related('person')
    data_source_query = data_source_query.filter(data_loader_id=data_loader_id)
    data_source_query = data_source_query.apply_permissions(request.authenticated_user, 'GET')

    data_source_query = data_source_query.distinct()

    response = [data_source for data_source in data_source_query.all()]

    return 200, response
