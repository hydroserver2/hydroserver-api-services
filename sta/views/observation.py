import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import (
    ObservationSummaryResponse,
    ObservationRowResponse,
    ObservationColumnarResponse,
    ObservationQueryParameters,
    ObservationPostBody,
    ObservationPatchBody,
    ObservationBulkPostBody,
    ObservationBulkPostQueryParameters,
    ObservationBulkDeleteBody,
)
from sta.services import ObservationService

observation_router = Router(tags=["Observations"])
observation_service = ObservationService()


@observation_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[ObservationSummaryResponse]
        | ObservationRowResponse
        | ObservationColumnarResponse,
        403: str,
        404: str,
    },
    by_alias=True,
)
def get_observations(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    datastream_id: Path[uuid.UUID],
    query: Query[ObservationQueryParameters],
):
    """
    Get Datastream Observations.
    """

    return 200, observation_service.list(
        principal=request.principal,
        response=response,
        datastream_id=datastream_id,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
        response_format=query.response_format,
    )


@observation_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: ObservationSummaryResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_observation(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    data: ObservationPostBody,
):
    """
    Create a new Observation.
    """

    return 201, observation_service.create(
        principal=request.principal, datastream_id=datastream_id, data=data
    )


@observation_router.post(
    "/bulk-create",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={201: None, 403: str, 404: str},
)
@transaction.atomic
def insert_observations(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    query: Query[ObservationBulkPostQueryParameters],
    data: ObservationBulkPostBody,
):
    """
    Insert Datastream Observations.
    """

    return 201, observation_service.bulk_create(
        principal=request.principal,
        datastream_id=datastream_id,
        data=data,
        mode=query.mode or "append",
    )


@observation_router.post(
    "/bulk-delete",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={204: None, 403: str, 404: str},
)
@transaction.atomic
def delete_observations(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    data: ObservationBulkDeleteBody,
):
    """
    Delete Datastream Observations between the given phenomenon start and end times.
    """

    return 204, observation_service.bulk_delete(
        principal=request.principal, datastream_id=datastream_id, data=data
    )


@observation_router.get(
    "/{observation_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: ObservationSummaryResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_observation(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    observation_id: Path[uuid.UUID],
):
    """
    Get an Observation.
    """

    return 200, observation_service.get(
        principal=request.principal, datastream_id=datastream_id, uid=observation_id
    )


@observation_router.patch(
    "/{observation_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: ObservationSummaryResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_observation(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    observation_id: Path[uuid.UUID],
    data: ObservationPatchBody,
):
    """
    Update an Observation.
    """

    return 200, observation_service.update(
        principal=request.principal,
        datastream_id=datastream_id,
        uid=observation_id,
        data=data,
    )


@observation_router.delete(
    "/{observation_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: None,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_observation(
    request: HydroServerHttpRequest,
    datastream_id: Path[uuid.UUID],
    observation_id: Path[uuid.UUID],
):
    """
    Delete an Observation.
    """

    return 204, observation_service.delete(
        principal=request.principal, datastream_id=datastream_id, uid=observation_id
    )
