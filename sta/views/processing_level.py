import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import (
    ProcessingLevelGetResponse,
    ProcessingLevelPostBody,
    ProcessingLevelPatchBody,
)
from sta.services import ProcessingLevelService

processing_level_router = Router(tags=["Processing Levels"])
processing_level_service = ProcessingLevelService()


@processing_level_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[ProcessingLevelGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_processing_levels(
    request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None
):
    """
    Get public Processing Levels and Processing Levels associated with the authenticated user.
    """

    return 200, processing_level_service.list(
        principal=request.principal, workspace_id=workspace_id
    )


@processing_level_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: ProcessingLevelGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_processing_level(
    request: HydroServerHttpRequest, data: ProcessingLevelPostBody
):
    """
    Create a new Processing Level.
    """

    return 201, processing_level_service.create(principal=request.principal, data=data)


@processing_level_router.get(
    "/{processing_level_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: ProcessingLevelGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_processing_level(
    request: HydroServerHttpRequest, processing_level_id: Path[uuid.UUID]
):
    """
    Get a Processing Level.
    """

    return 200, processing_level_service.get(
        principal=request.principal, uid=processing_level_id
    )


@processing_level_router.patch(
    "/{processing_level_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: ProcessingLevelGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_processing_level(
    request: HydroServerHttpRequest,
    processing_level_id: Path[uuid.UUID],
    data: ProcessingLevelPatchBody,
):
    """
    Update a Processing Level.
    """

    return 200, processing_level_service.update(
        principal=request.principal, uid=processing_level_id, data=data
    )


@processing_level_router.delete(
    "/{processing_level_id}",
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
def delete_processing_level(
    request: HydroServerHttpRequest, processing_level_id: Path[uuid.UUID]
):
    """
    Delete a Processing Level.
    """

    return 204, processing_level_service.delete(
        principal=request.principal, uid=processing_level_id
    )
