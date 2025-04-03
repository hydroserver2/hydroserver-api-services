import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import EtlSystemGetResponse, EtlSystemPostBody, EtlSystemPatchBody
from etl.services import EtlSystemService

etl_system_router = Router(tags=["ETL Systems"])
etl_system_service = EtlSystemService()


@etl_system_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[EtlSystemGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_etl_systems(
    request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None
):
    """
    Get public ETL Systems and ETL Systems associated with the authenticated user.
    """

    return 200, etl_system_service.list(
        user=request.authenticated_user, workspace_id=workspace_id
    )


@etl_system_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: EtlSystemGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_etl_system(request: HydroServerHttpRequest, data: EtlSystemPostBody):
    """
    Create a new ETL System.
    """

    return 201, etl_system_service.create(user=request.authenticated_user, data=data)


@etl_system_router.get(
    "/{etl_system_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: EtlSystemGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_etl_system(request: HydroServerHttpRequest, etl_system_id: Path[uuid.UUID]):
    """
    Get an ETL System.
    """

    return 200, etl_system_service.get(
        user=request.authenticated_user, uid=etl_system_id
    )


@etl_system_router.patch(
    "/{etl_system_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: EtlSystemGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_etl_system(
    request: HydroServerHttpRequest,
    etl_system_id: Path[uuid.UUID],
    data: EtlSystemPatchBody,
):
    """
    Update an ETL System.
    """

    return 200, etl_system_service.update(
        user=request.authenticated_user, uid=etl_system_id, data=data
    )


@etl_system_router.delete(
    "/{etl_system_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_etl_system(request: HydroServerHttpRequest, etl_system_id: Path[uuid.UUID]):
    """
    Delete an ETL System.
    """

    return 204, etl_system_service.delete(
        user=request.authenticated_user, uid=etl_system_id
    )
