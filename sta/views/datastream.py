import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import DatastreamGetResponse, DatastreamPostBody, DatastreamPatchBody
from sta.services import DatastreamService

datastream_router = Router(tags=["Datastreams"])
datastream_service = DatastreamService()


@datastream_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[DatastreamGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_datastreams(
    request: HydroServerHttpRequest,
    workspace_id: Optional[uuid.UUID] = None,
    thing_id: Optional[uuid.UUID] = None,
):
    """
    Get public Datastreams and Datastreams associated with the authenticated user.
    """

    return 200, datastream_service.list(
        user=request.authenticated_user, workspace_id=workspace_id, thing_id=thing_id
    )


@datastream_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: DatastreamGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_datastream(request: HydroServerHttpRequest, data: DatastreamPostBody):
    """
    Create a new Datastream.
    """

    return 201, datastream_service.create(user=request.authenticated_user, data=data)


@datastream_router.get(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: DatastreamGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_datastream(request: HydroServerHttpRequest, datastream_id: Path[uuid.UUID]):
    """
    Get a Datastream.
    """

    return 200, datastream_service.get(
        user=request.authenticated_user, uid=datastream_id
    )


@datastream_router.patch(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: DatastreamGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_datastream(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    data: DatastreamPatchBody,
):
    """
    Update a Datastream.
    """

    return 200, datastream_service.update(
        user=request.authenticated_user, uid=datastream_id, data=data
    )


@datastream_router.delete(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_datastream(request: HydroServerHttpRequest, datastream_id: Path[uuid.UUID]):
    """
    Delete a Datastream.
    """

    return 204, datastream_service.delete(
        user=request.authenticated_user, uid=datastream_id
    )


@datastream_router.get(
    "/{datastream_id}/csv",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={200: None, 403: str, 404: str},
)
def get_datastream_csv(request: HydroServerHttpRequest, datastream_id: Path[uuid.UUID]):
    """
    Get a CSV representation of the Datastream.
    """

    return datastream_service.get_csv(
        user=request.authenticated_user, uid=datastream_id
    )


@datastream_router.get(
    "/{datastream_id}/observations",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={200: list[list], 403: str, 404: str},
)
def get_datastream_observations(request: HydroServerHttpRequest, datastream_id: Path[uuid.UUID]):
    """
    Get Datastream Observations
    """

    return datastream_service.list_observations(
        user=request.authenticated_user, uid=datastream_id
    )
