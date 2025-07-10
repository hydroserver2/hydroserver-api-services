import uuid
from ninja import Router, Path, Query
from django.db import transaction
from django.http import HttpResponse
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from api.schemas import VocabularyQueryParameters
from sta.schemas import (
    UnitSummaryResponse,
    UnitDetailResponse,
    UnitPostBody,
    UnitPatchBody,
    UnitQueryParameters,
)
from sta.services import UnitService

unit_router = Router(tags=["Units"])
unit_service = UnitService()


@unit_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[UnitSummaryResponse],
        401: str,
    },
    by_alias=True,
)
def get_units(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[UnitQueryParameters],
):
    """
    Get public Units and Units associated with the authenticated user.
    """

    return 200, unit_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
    )


@unit_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: UnitSummaryResponse,
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
    "/types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_unit_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get unit types.
    """

    return 200, unit_service.list_unit_types(
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@unit_router.get(
    "/{unit_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: UnitDetailResponse,
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
        200: UnitSummaryResponse,
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
