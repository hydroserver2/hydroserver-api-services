from ninja import Router, Path
from typing import List
from uuid import UUID
from django.db import transaction, IntegrityError
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import DataSource
from .schemas import DataSourceGetResponse, DataSourcePostBody, DataSourcePatchBody, \
    DataSourceFields
from .utils import query_data_sources, get_data_source_by_id, build_data_source_response


router = Router(tags=['Data Sources'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[DataSourceGetResponse]
    },
    by_alias=True
)
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


@router.get(
    '{data_source_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: DataSourceGetResponse,
        404: str
    },
    by_alias=True
)
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


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: DataSourceGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
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


@router.patch(
    '{data_source_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: DataSourceGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
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


@router.delete(
    '{data_source_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        409: str
    }
)
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
