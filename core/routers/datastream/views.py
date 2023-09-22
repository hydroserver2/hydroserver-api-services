from ninja import Router, Path
from typing import List
from uuid import UUID
from django.db import transaction, IntegrityError
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from accounts.auth.anonymous import anonymous_auth
from core.routers.thing.utils import check_thing_by_id
from core.models import Datastream
from .schemas import DatastreamFields, DatastreamGetResponse, DatastreamPostBody, DatastreamPatchBody
from .utils import query_datastreams, get_datastream_by_id, build_datastream_response, check_related_fields


router = Router(tags=['Datastreams'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth(), anonymous_auth],
    response={
        200: List[DatastreamGetResponse]
    },
    by_alias=True
)
def get_datastreams(request):
    """
    Get a list of Datastreams

    This endpoint returns a list of public Datastreams and Datastreams owned by the authenticated user if there is one.
    """

    datastream_query, _ = query_datastreams(user=request.authenticated_user)

    return [
        build_datastream_response(datastream) for datastream in datastream_query.all()
    ]


@router.get(
    '{datastream_id}',
    auth=[JWTAuth(), BasicAuth(), anonymous_auth],
    response={
        200: DatastreamGetResponse,
        404: str
    },
    by_alias=True
)
def get_datastream(request, datastream_id: UUID = Path(...)):
    """
    Get details for a Datastream

    This endpoint returns details for a Datastream given a Datastream ID.
    """

    datastream = get_datastream_by_id(
        user=request.authenticated_user,
        datastream_id=datastream_id,
        raise_http_errors=True
    )

    return 200, build_datastream_response(datastream)


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: DatastreamGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def create_datastream(request, data: DatastreamPostBody):
    """
    Create a Datastream

    This endpoint will create a new Datastream.
    """

    check_related_fields(request.authenticated_user, data)

    datastream = Datastream.objects.create(
        **data.dict(include=set(DatastreamFields.__fields__.keys()))
    )

    datastream = get_datastream_by_id(
        user=request.authenticated_user,
        datastream_id=datastream.id,
    )

    return 201, build_datastream_response(datastream)


@router.patch(
    '{datastream_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: DatastreamGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_datastream(request, data: DatastreamPatchBody, datastream_id: UUID = Path(...)):
    """
    Update a Datastream

    This endpoint will update an existing Datastream owned by the authenticated user and return the updated Datastream.
    """

    check_related_fields(request.authenticated_user, data)

    datastream = get_datastream_by_id(
        user=request.authenticated_user,
        datastream_id=datastream_id,
        require_ownership=True,
        raise_http_errors=True
    )

    datastream_data = data.dict(include=set(DatastreamFields.__fields__.keys()), exclude_unset=True)

    for field, value in datastream_data.items():
        setattr(datastream, field, value)

    datastream.save()

    datastream = get_datastream_by_id(user=request.authenticated_user, datastream_id=datastream.id)

    return 203, build_datastream_response(datastream)


@router.delete(
    '{datastream_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        409: str
    }
)
def delete_datastream(request, datastream_id: UUID = Path(...)):
    """
    Delete a Datastream

    This endpoint will delete an existing Datastream if the authenticated user is the primary owner of the Datastream.
    """

    datastream = get_datastream_by_id(
        user=request.authenticated_user,
        datastream_id=datastream_id,
        require_primary_ownership=True,
        raise_http_errors=True
    )

    try:
        datastream.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
