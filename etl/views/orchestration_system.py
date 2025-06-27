import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import (
    OrchestrationSystemGetResponse,
    OrchestrationSystemQueryParameters,
    OrchestrationSystemPostBody,
    OrchestrationSystemPatchBody,
)
from etl.services import OrchestrationSystemService

orchestration_system_router = Router(tags=["Orchestration Systems"])
orchestration_system_service = OrchestrationSystemService()


@orchestration_system_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[OrchestrationSystemGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_orchestration_systems(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[OrchestrationSystemQueryParameters],
):
    """
    Get public Orchestration Systems and Orchestration Systems associated with the authenticated user.
    """

    return 200, orchestration_system_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        ordering=query.ordering,
        filtering=query.dict(exclude_unset=True),
    )


@orchestration_system_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: OrchestrationSystemGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_orchestration_system(
    request: HydroServerHttpRequest, data: OrchestrationSystemPostBody
):
    """
    Create a new Orchestration System.
    """

    return 201, orchestration_system_service.create(
        principal=request.principal, data=data
    )


@orchestration_system_router.get(
    "/{orchestration_system_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: OrchestrationSystemGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_orchestration_system(
    request: HydroServerHttpRequest, orchestration_system_id: Path[uuid.UUID]
):
    """
    Get an Orchestration System.
    """

    return 200, orchestration_system_service.get(
        principal=request.principal, uid=orchestration_system_id
    )


@orchestration_system_router.patch(
    "/{orchestration_system_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: OrchestrationSystemGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_orchestration_system(
    request: HydroServerHttpRequest,
    orchestration_system_id: Path[uuid.UUID],
    data: OrchestrationSystemPatchBody,
):
    """
    Update an Orchestration System.
    """

    return 200, orchestration_system_service.update(
        principal=request.principal, uid=orchestration_system_id, data=data
    )


@orchestration_system_router.delete(
    "/{orchestration_system_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: str,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_orchestration_system(
    request: HydroServerHttpRequest, orchestration_system_id: Path[uuid.UUID]
):
    """
    Delete an Orchestration System.
    """

    return 204, orchestration_system_service.delete(
        principal=request.principal, uid=orchestration_system_id
    )
