from ninja import Path
from uuid import UUID
from django.db import transaction, IntegrityError
from core.router import DataManagementRouter
from core.models import DataSource
from core.endpoints.datastream.schemas import DatastreamGetResponse
from core.endpoints.datastream.utils import query_datastreams, build_datastream_response
from .schemas import DataSourceGetResponse, DataSourcePostBody, DataSourcePatchBody, \
    DataSourceFields
from .utils import query_data_sources, get_data_source_by_id, build_data_source_response, check_data_source_by_id


router = DataManagementRouter(tags=['Data Sources'])


@router.dm_list('', response=DataSourceGetResponse)
def get_data_sources(request):
    """
    Get a list of Data Sources

    This endpoint returns a list of Data Sources owned by the authenticated user.
    """

    data_source_query, _ = query_data_sources(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    return [
        build_data_source_response(data_source) for data_source in data_source_query.all()
    ]


@router.dm_get('{data_source_id}', response=DataSourceGetResponse)
def get_data_source(request, data_source_id: UUID = Path(...)):
    """
    Get details for a Data Source

    This endpoint returns details for a Data Source given a Data Source ID.
    """

    data_source = get_data_source_by_id(
        user=request.authenticated_user,
        data_source_id=data_source_id,
        raise_http_errors=True
    )

    return 200, build_data_source_response(data_source)


@router.dm_post('', response=DataSourceGetResponse)
@transaction.atomic
def create_data_source(request, data: DataSourcePostBody):
    """
    Create a Data Source

    This endpoint will create a new Data Source owned by the authenticated user and returns the created Processing
    Level.
    """

    data_source = DataSource.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(DataSourceFields.__fields__.keys()))
    )

    data_source = get_data_source_by_id(
        user=request.authenticated_user,
        data_source_id=data_source.id,
        raise_http_errors=True
    )

    return 201, build_data_source_response(data_source)


@router.dm_patch('{data_source_id}', response=DataSourceGetResponse)
@transaction.atomic
def update_data_source(request, data: DataSourcePatchBody, data_source_id: UUID = Path(...)):
    """
    Update a Data Source

    This endpoint will update an existing Data Source owned by the authenticated user and return the updated
    Data Source.
    """

    data_source = get_data_source_by_id(
        user=request.authenticated_user,
        data_source_id=data_source_id,
        require_ownership=True,
        raise_http_errors=True
    )

    data_source_data = data.dict(include=set(DataSourceFields.__fields__.keys()), exclude_unset=True)

    for field, value in data_source_data.items():
        setattr(data_source, field, value)

    data_source.save()

    data_source = get_data_source_by_id(
        user=request.authenticated_user,
        data_source_id=data_source_id
    )

    return 203, build_data_source_response(data_source)


@router.dm_delete('{data_source_id}')
@transaction.atomic
def delete_data_source(request, data_source_id: UUID = Path(...)):
    """
    Delete a Data Source

    This endpoint will delete an existing Data Source if the authenticated user is the primary owner of the
    Data Source.
    """

    data_source = get_data_source_by_id(
        user=request.authenticated_user,
        data_source_id=data_source_id,
        require_ownership=True,
        raise_http_errors=True
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

    This endpoint returns a list of public Datastreams and Datastreams owned by the authenticated user if there is one
    associated with the given Data Source ID.
    """

    check_data_source_by_id(
        user=request.authenticated_user,
        data_source_id=data_source_id,
        raise_http_errors=True
    )

    datastream_query, _ = query_datastreams(
        user=request.authenticated_user,
        data_source_ids=[data_source_id]
    )

    return [
        build_datastream_response(datastream) for datastream in datastream_query.all()
    ]
