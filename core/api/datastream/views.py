from ninja import Path
from uuid import UUID
from django.db import transaction, IntegrityError
from core.router import DataManagementRouter
from core.models import Datastream
from .schemas import DatastreamFields, DatastreamGetResponse, DatastreamPostBody, DatastreamPatchBody
from .utils import query_datastreams, get_datastream_by_id, build_datastream_response, check_related_fields


router = DataManagementRouter(tags=['Datastreams'])


@router.dm_list('', response=DatastreamGetResponse)
def get_datastreams(request):
    """
    Get a list of Datastreams

    This endpoint returns a list of public Datastreams and Datastreams owned by the authenticated user if there is one.
    """

    datastream_query, _ = query_datastreams(user=request.authenticated_user)

    return [
        build_datastream_response(datastream) for datastream in datastream_query.all()
    ]


@router.dm_get('{datastream_id}', response=DatastreamGetResponse)
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


@router.dm_post('', response=DatastreamGetResponse)
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


@router.dm_patch('{datastream_id}', response=DatastreamGetResponse)
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


@router.dm_delete('{datastream_id}')
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
