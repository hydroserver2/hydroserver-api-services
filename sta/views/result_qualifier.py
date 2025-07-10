import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import (
    ResultQualifierSummaryResponse,
    ResultQualifierDetailResponse,
    ResultQualifierQueryParameters,
    ResultQualifierPostBody,
    ResultQualifierPatchBody,
)
from sta.services import ResultQualifierService

result_qualifier_router = Router(tags=["Result Qualifiers"])
result_qualifier_service = ResultQualifierService()


@result_qualifier_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[ResultQualifierSummaryResponse],
        401: str,
    },
    by_alias=True,
)
def get_result_qualifiers(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[ResultQualifierQueryParameters],
):
    """
    Get public Result Qualifiers and Result Qualifiers associated with the authenticated user.
    """

    return 200, result_qualifier_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
    )


@result_qualifier_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: ResultQualifierSummaryResponse,
        401: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_result_qualifier(
    request: HydroServerHttpRequest, data: ResultQualifierPostBody
):
    """
    Create a new Result Qualifier.
    """

    return 201, result_qualifier_service.create(principal=request.principal, data=data)


@result_qualifier_router.get(
    "/{result_qualifier_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: ResultQualifierDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_result_qualifier(
    request: HydroServerHttpRequest, result_qualifier_id: Path[uuid.UUID]
):
    """
    Get a Result Qualifier.
    """

    return 200, result_qualifier_service.get(
        principal=request.principal, uid=result_qualifier_id
    )


@result_qualifier_router.patch(
    "/{result_qualifier_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: ResultQualifierSummaryResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_result_qualifier(
    request: HydroServerHttpRequest,
    result_qualifier_id: Path[uuid.UUID],
    data: ResultQualifierPatchBody,
):
    """
    Update a Result Qualifier.
    """

    return 200, result_qualifier_service.update(
        principal=request.principal, uid=result_qualifier_id, data=data
    )


@result_qualifier_router.delete(
    "/{result_qualifier_id}",
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
def delete_result_qualifier(
    request: HydroServerHttpRequest, result_qualifier_id: Path[uuid.UUID]
):
    """
    Delete a Result Qualifier.
    """

    return 204, result_qualifier_service.delete(
        principal=request.principal, uid=result_qualifier_id
    )
