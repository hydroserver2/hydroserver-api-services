import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from api.schemas import VocabularyQueryParameters
from sta.schemas import (
    DatastreamSummaryResponse,
    DatastreamDetailResponse,
    DatastreamQueryParameters,
    DatastreamPostBody,
    DatastreamPatchBody
)
from sta.services import DatastreamService

datastream_router = Router(tags=["Datastreams"])
datastream_service = DatastreamService()


@datastream_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[DatastreamSummaryResponse],
        401: str,
    },
    by_alias=True,
)
def get_datastreams(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[DatastreamQueryParameters],
):
    """
    Get public Datastreams and Datastreams associated with the authenticated user.
    """

    return 200, datastream_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
    )


@datastream_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: DatastreamSummaryResponse,
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
    "/aggregation-statistics",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_datastream_aggregation_statistics(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get datastream aggregation statistics.
    """

    return 200, datastream_service.list_aggregation_statistics(
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@datastream_router.get(
    "/statuses",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_datastream_statuses(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get datastream statuses.
    """

    return 200, datastream_service.list_statuses(
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@datastream_router.get(
    "/sampled-mediums",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_datastream_sampled_mediums(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get datastream sampled mediums.
    """

    return 200, datastream_service.list_sampled_mediums(
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@datastream_router.get(
    "/{datastream_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: DatastreamDetailResponse,
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
        200: DatastreamSummaryResponse,
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
