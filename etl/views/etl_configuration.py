import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import (
    EtlConfigurationGetResponse,
    EtlConfigurationPostBody,
    EtlConfigurationPatchBody,
)
from etl.services import EtlConfigurationService

etl_configuration_router = Router(tags=["ETL Configurations"])
etl_configuration_service = EtlConfigurationService()


@etl_configuration_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[EtlConfigurationGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_etl_configurations(
    request: HydroServerHttpRequest,
    etl_system_platform_id: Path[uuid.UUID],
    workspace_id: Optional[uuid.UUID] = None,
):
    """
    Get public ETL Configurations and ETL Configurations associated with the authenticated user.
    """

    return 200, etl_configuration_service.list(
        user=request.authenticated_user,
        etl_system_platform_id=etl_system_platform_id,
        workspace_id=workspace_id,
    )


@etl_configuration_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: EtlConfigurationGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_etl_configuration(
    request: HydroServerHttpRequest,
    etl_system_platform_id: Path[uuid.UUID],
    data: EtlConfigurationPostBody,
):
    """
    Create a new ETL Configuration.
    """

    return 201, etl_configuration_service.create(
        user=request.authenticated_user,
        etl_system_platform_id=etl_system_platform_id,
        data=data,
    )


@etl_configuration_router.get(
    "/{etl_configuration_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: EtlConfigurationGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_etl_configuration(
    request: HydroServerHttpRequest,
    etl_system_platform_id: Path[uuid.UUID],
    etl_configuration_id: Path[uuid.UUID],
):
    """
    Get an ETL Configuration.
    """

    return 200, etl_configuration_service.get(
        user=request.authenticated_user,
        uid=etl_configuration_id,
        etl_system_platform_id=etl_system_platform_id,
    )


@etl_configuration_router.patch(
    "/{etl_configuration_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: EtlConfigurationGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_etl_configuration(
    request: HydroServerHttpRequest,
    etl_system_platform_id: Path[uuid.UUID],
    etl_configuration_id: Path[uuid.UUID],
    data: EtlConfigurationPatchBody,
):
    """
    Update an ETL Configuration.
    """

    return 200, etl_configuration_service.update(
        user=request.authenticated_user,
        uid=etl_configuration_id,
        etl_system_platform_id=etl_system_platform_id,
        data=data,
    )


@etl_configuration_router.delete(
    "/{etl_configuration_id}",
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
def delete_etl_configuration(
    request: HydroServerHttpRequest,
    etl_system_platform_id: Path[uuid.UUID],
    etl_configuration_id: Path[uuid.UUID],
):
    """
    Delete an ETL Configuration.
    """

    return 204, etl_configuration_service.delete(
        user=request.authenticated_user,
        uid=etl_configuration_id,
        etl_system_platform_id=etl_system_platform_id,
    )
