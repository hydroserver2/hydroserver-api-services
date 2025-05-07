import uuid
from ninja import Router, Path
from typing import Optional, Literal
from datetime import datetime
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import (
    DatastreamGetResponse,
    DatastreamPostBody,
    DatastreamPatchBody,
    ObservationsGetResponse,
)
from sta.services import DatastreamService

datastream_router = Router(tags=["Datastreams"])
datastream_service = DatastreamService()


@datastream_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
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
        principal=request.principal, workspace_id=workspace_id, thing_id=thing_id
    )


@datastream_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
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

    return 201, datastream_service.create(principal=request.principal, data=data)


@datastream_router.get(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
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

    return 200, datastream_service.get(principal=request.principal, uid=datastream_id)


@datastream_router.patch(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
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
        principal=request.principal, uid=datastream_id, data=data
    )


@datastream_router.delete(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
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
        principal=request.principal, uid=datastream_id
    )


@datastream_router.get(
    "/{datastream_id}/csv",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={200: None, 403: str, 404: str},
)
def get_datastream_csv(request: HydroServerHttpRequest, datastream_id: Path[uuid.UUID]):
    """
    Get a CSV representation of the Datastream.
    """

    return datastream_service.get_csv(principal=request.principal, uid=datastream_id)


@datastream_router.get(
    "/{datastream_id}/observations",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={200: ObservationsGetResponse, 403: str, 404: str},
)
def get_datastream_observations(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    phenomenon_start_time: Optional[datetime] = None,
    phenomenon_end_time: Optional[datetime] = None,
    page: int = 1,
    page_size: Optional[int] = None,
    order: Literal["asc", "desc"] = "desc",
):
    """
    Get Datastream Observations
    """

    return datastream_service.list_observations(
        principal=request.principal,
        uid=datastream_id,
        phenomenon_start_time=phenomenon_start_time,
        phenomenon_end_time=phenomenon_end_time,
        page=page,
        page_size=page_size,
        order=order,
    )
