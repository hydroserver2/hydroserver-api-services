import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import EtlSystemPlatformGetResponse, EtlSystemPlatformPostBody, EtlSystemPlatformPatchBody
from etl.services import EtlSystemPlatformService

etl_system_platform_router = Router(tags=["ETL System Platforms"])
etl_system_platform_service = EtlSystemPlatformService()


@etl_system_platform_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[EtlSystemPlatformGetResponse],
        401: str,
    },
    by_alias=True
)
def get_etl_system_platforms(request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None):
    """
    Get public ETL System Platforms and ETL System Platforms associated with the authenticated user.
    """

    return 200, etl_system_platform_service.list(
        user=request.authenticated_user,
        workspace_id=workspace_id
    )


@etl_system_platform_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: EtlSystemPlatformGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
@transaction.atomic
def create_etl_system_platform(request: HydroServerHttpRequest, data: EtlSystemPlatformPostBody):
    """
    Create a new ETL System Platform.
    """

    return 201, etl_system_platform_service.create(
        user=request.authenticated_user,
        data=data
    )


@etl_system_platform_router.get(
    "/{etl_system_platform_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: EtlSystemPlatformGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True
)
def get_etl_system_platform(request: HydroServerHttpRequest, etl_system_platform_id: Path[uuid.UUID]):
    """
    Get an ETL System Platform.
    """

    return 200, etl_system_platform_service.get(
        user=request.authenticated_user,
        uid=etl_system_platform_id
    )


@etl_system_platform_router.patch(
    "/{etl_system_platform_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: EtlSystemPlatformGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
@transaction.atomic
def update_etl_system_platform(request: HydroServerHttpRequest, etl_system_platform_id: Path[uuid.UUID],
                               data: EtlSystemPlatformPatchBody):
    """
    Update an ETL System Platform.
    """

    return 200, etl_system_platform_service.update(
        user=request.authenticated_user,
        uid=etl_system_platform_id,
        data=data
    )


@etl_system_platform_router.delete(
    "/{etl_system_platform_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True
)
@transaction.atomic
def delete_etl_system_platform(request: HydroServerHttpRequest, etl_system_platform_id: Path[uuid.UUID]):
    """
    Delete an ETL System Platform.
    """

    return 204, etl_system_platform_service.delete(
        user=request.authenticated_user,
        uid=etl_system_platform_id
    )
