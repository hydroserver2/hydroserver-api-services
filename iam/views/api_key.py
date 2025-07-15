import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.http import HydroServerHttpRequest
from hydroserver.security import bearer_auth, session_auth, apikey_auth
from iam.schemas import (
    APIKeyDetailResponse,
    APIKeyQueryParameters,
    APIKeyPostBody,
    APIKeyPatchBody,
    APIKeyPostResponse,
)
from iam.services import APIKeyService

api_key_router = Router(tags=["API Keys"])
api_key_service = APIKeyService()


@api_key_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: list[APIKeyDetailResponse],
        401: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_api_keys(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    workspace_id: Path[uuid.UUID],
    query: Query[APIKeyQueryParameters],
):
    """
    Get API keys associated with the authenticated user.
    """

    return 200, api_key_service.list(
        principal=request.principal,
        response=response,
        workspace_id=workspace_id,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
    )


@api_key_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: APIKeyPostResponse,
        401: str,
        422: str,
    },
    by_alias=True,
    exclude_unset=True,
)
@transaction.atomic
def create_api_key(
    request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID], data: APIKeyPostBody
):
    """
    Create a new API key for the workspace.
    """

    return 201, api_key_service.create(
        principal=request.principal, workspace_id=workspace_id, data=data
    )


@api_key_router.get(
    "/{api_key_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: APIKeyDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_api_key(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    api_key_id: Path[uuid.UUID],
):
    """
    Get API key details.
    """

    return 200, api_key_service.get(
        principal=request.principal, workspace_id=workspace_id, uid=api_key_id
    )


@api_key_router.patch(
    "/{api_key_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: APIKeyDetailResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
    exclude_unset=True,
)
@transaction.atomic
def update_api_key(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    api_key_id: Path[uuid.UUID],
    data: APIKeyPatchBody,
):
    """
    Update an API key.
    """

    return 200, api_key_service.update(
        principal=request.principal,
        workspace_id=workspace_id,
        uid=api_key_id,
        data=data,
    )


@api_key_router.delete(
    "/{api_key_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: None,
        401: str,
        403: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_api_key(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    api_key_id: Path[uuid.UUID],
):
    """
    Delete an API key.
    """

    return 204, api_key_service.delete(
        principal=request.principal, workspace_id=workspace_id, uid=api_key_id
    )


@api_key_router.put(
    "/{api_key_id}/regenerate",
    auth=[session_auth, bearer_auth],
    response={
        201: APIKeyPostResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def regenerate_api_key(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    api_key_id: Path[uuid.UUID],
):
    """
    Regenerate an API key using existing settings.
    """

    return 201, api_key_service.regenerate(
        principal=request.principal, workspace_id=workspace_id, uid=api_key_id
    )
