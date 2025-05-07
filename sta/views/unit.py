import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import UnitGetResponse, UnitPostBody, UnitPatchBody
from sta.services import UnitService

unit_router = Router(tags=["Units"])
unit_service = UnitService()


@unit_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[UnitGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_units(
    request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None
):
    """
    Get public Units and Units associated with the authenticated user.
    """

    return 200, unit_service.list(
        principal=request.principal, workspace_id=workspace_id
    )


@unit_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: UnitGetResponse,
        400: str,
        401: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_unit(request: HydroServerHttpRequest, data: UnitPostBody):
    """
    Create a new Unit.
    """

    return 201, unit_service.create(principal=request.principal, data=data)


@unit_router.get(
    "/{unit_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: UnitGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_unit(request: HydroServerHttpRequest, unit_id: Path[uuid.UUID]):
    """
    Get a Unit.
    """

    return 200, unit_service.get(principal=request.principal, uid=unit_id)


@unit_router.patch(
    "/{unit_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: UnitGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_unit(
    request: HydroServerHttpRequest, unit_id: Path[uuid.UUID], data: UnitPatchBody
):
    """
    Update a Unit.
    """

    return 200, unit_service.update(principal=request.principal, uid=unit_id, data=data)


@unit_router.delete(
    "/{unit_id}",
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
def delete_unit(request: HydroServerHttpRequest, unit_id: Path[uuid.UUID]):
    """
    Delete a Unit.
    """

    return 204, unit_service.delete(principal=request.principal, uid=unit_id)
