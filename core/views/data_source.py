from ninja import Path
from uuid import UUID
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import DataSource, DataLoader, Datastream
from core.schemas.data_source import DataSourceGetResponse, DataSourcePostBody, DataSourcePatchBody, \
    DataSourceFields
from core.schemas.datastream import DatastreamGetResponse


router = DataManagementRouter(tags=['Data Sources'])


@router.dm_list('', response=DataSourceGetResponse)
def get_data_sources(request):
    """
    Get a list of Data Sources

    This endpoint returns a list of data sources owned by the authenticated user.
    """

    data_source_query = DataSource.objects.select_related('person')
    data_source_query = data_source_query.filter(person__is_active=True)
    data_source_query = data_source_query.filter(Q(person=request.authenticated_user))
    data_source_query = data_source_query.apply_permissions(request.authenticated_user, 'GET')

    data_source_query = data_source_query.distinct()

    response = [data_source for data_source in data_source_query.all()]

    return 200, response


@router.dm_get('{data_source_id}', response=DataSourceGetResponse)
def get_data_source(request, data_source_id: UUID = Path(...)):
    """
    Get details for a Data Source

    This endpoint returns details for a data source given a data source ID.
    """

    data_source = DataSource.objects.get_by_id(
        data_source_id=data_source_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, data_source


@router.dm_post('', response=DataSourceGetResponse)
@transaction.atomic
def create_data_source(request, data: DataSourcePostBody):
    """
    Create a Data Source

    This endpoint will create a new data source owned by the authenticated user and returns the created data source.
    """

    data_source_data = data.dict(include=set(DataSourceFields.model_fields.keys()))

    if data_source_data.get('data_loader_id') and not DataLoader.objects.get_by_id(
        data_loader_id=data_source_data['data_loader_id'],
        user=request.authenticated_user,
        method='POST',
        model='DataSource'
    ):
        return 403, 'You do not have permission to link a data source to the given data loader.'

    data_source = DataSource.objects.create(
        person=request.authenticated_user,
        **data_source_data
    )

    return 201, data_source


@router.dm_patch('{data_source_id}', response=DataSourceGetResponse)
@transaction.atomic
def update_data_source(request, data: DataSourcePatchBody, data_source_id: UUID = Path(...)):
    """
    Update a Data Source

    This endpoint will update an existing data source owned by the authenticated user and return the updated
    data source.
    """

    data_source = DataSource.objects.get_by_id(
        data_source_id=data_source_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    data_source_data = data.dict(include=set(DataSourceFields.model_fields.keys()), exclude_unset=True)

    if data_source_data.get('data_loader_id') and not DataLoader.objects.get_by_id(
        data_loader_id=data_source_data['data_loader_id'],
        user=request.authenticated_user,
        method='PATCH',
        model='DataSource'
    ):
        return 403, 'You do not have permission to link a data source to the given data loader.'

    if not request.authenticated_user.permissions.check_allowed_fields(
            'DataSource', fields=[*data_source_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this data source.'

    for field, value in data_source_data.items():
        setattr(data_source, field, value)

    data_source.save()

    return 203, data_source


@router.dm_delete('{data_source_id}')
@transaction.atomic
def delete_data_source(request, data_source_id: UUID = Path(...)):
    """
    Delete a Data Source

    This endpoint will delete an existing data source if the authenticated user is the primary owner of the
    data source.
    """

    data_source = DataSource.objects.get_by_id(
        data_source_id=data_source_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        data_source.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None


@router.dm_list(
    '{data_source_id}/datastreams',
    response=DatastreamGetResponse
)
def get_datasource_datastreams(request, data_source_id: UUID = Path(...)):
    """
    Get a list of Datastreams for a Data Source

    This endpoint returns a list of public datastreams and datastreams owned by the authenticated user if there is one
    associated with the given data source ID.
    """

    DataSource.objects.get_by_id(
        data_source_id=data_source_id,
        user=request.authenticated_user,
        method='GET',
        model='Datastream',
        raise_404=True,
        fetch=True
    )

    datastream_query = Datastream.objects.select_related('processing_level', 'unit')

    if request.authenticated_user and request.authenticated_user.permissions.enabled():
        datastream_query = datastream_query.apply_permissions(user=request.authenticated_user, method='GET')

    datastream_query = datastream_query.filter(data_source_id=data_source_id)
    datastream_query = datastream_query.distinct()

    response = [datastream for datastream in datastream_query.all()]

    return 200, response
