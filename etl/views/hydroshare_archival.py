import uuid
from ninja import Router, Path
from typing import Optional
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from etl.schemas import (
    HydroShareArchivalDetailResponse,
    HydroShareArchivalPostBody,
    HydroShareArchivalPatchBody,
)
from etl.services import HydroShareArchivalService

hydroshare_archival_router = Router(tags=["HydroShare Archival"])
hydroshare_archival_service = HydroShareArchivalService()


@hydroshare_archival_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: Optional[HydroShareArchivalDetailResponse],
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_thing_archive(request, thing_id: Path[uuid.UUID]):
    """
    Get HydroShare archival details for a thing.
    """

    return 200, hydroshare_archival_service.get(
        principal=request.principal, uid=thing_id
    )


@hydroshare_archival_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: HydroShareArchivalDetailResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def create_thing_archive(
    request, data: HydroShareArchivalPostBody, thing_id: Path[uuid.UUID]
):
    """
    Create a HydroShare data archive for a thing.
    """

    return 201, hydroshare_archival_service.create(
        principal=request.principal, uid=thing_id, data=data
    )


@hydroshare_archival_router.post(
    "/trigger",
    auth=[session_auth, bearer_auth],
    response={
        200: HydroShareArchivalDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def run_thing_archival(request, thing_id: Path[uuid.UUID]):
    """
    Archive thing data to HydroShare.
    """

    return 200, hydroshare_archival_service.run(
        principal=request.principal, uid=thing_id
    )


@hydroshare_archival_router.patch(
    "",
    auth=[session_auth, bearer_auth],
    response={
        200: HydroShareArchivalDetailResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def update_archive(
    request, data: HydroShareArchivalPatchBody, thing_id: Path[uuid.UUID]
):
    """
    Update HydroShare data archive details for a thing.
    """

    return 200, hydroshare_archival_service.update(
        principal=request.principal, uid=thing_id, data=data
    )


@hydroshare_archival_router.delete(
    "",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def delete_archive(request, thing_id: Path[uuid.UUID]):
    """
    Delete a HydroShare data archive for a thing. Note: This will not delete the HydroShare resource.
    """

    return 204, hydroshare_archival_service.delete(
        principal=request.principal, uid=thing_id
    )
