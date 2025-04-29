import uuid
from ninja import Router, Path
from django.db import transaction
from hydroserver.http import HydroServerHttpRequest
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from iam.schemas import (
    WorkspaceGetResponse,
    WorkspacePostBody,
    WorkspacePatchBody,
    WorkspaceTransferBody,
)
from iam.services import WorkspaceService

workspace_router = Router(tags=["Workspaces"])
workspace_service = WorkspaceService()


@workspace_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[WorkspaceGetResponse],
        401: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_workspaces(request: HydroServerHttpRequest, associated_only: bool = False):
    """
    Get public workspaces and workspaces associated with the authenticated user.
    """

    return 200, workspace_service.list(
        user=request.authenticated_user, associated_only=associated_only
    )


@workspace_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: WorkspaceGetResponse,
        401: str,
        422: str,
    },
    by_alias=True,
    exclude_unset=True,
)
@transaction.atomic
def create_workspace(request: HydroServerHttpRequest, data: WorkspacePostBody):
    """
    Create a new workspace owned by the authenticated user.
    """

    return 201, workspace_service.create(user=request.authenticated_user, data=data)


@workspace_router.get(
    "/{workspace_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: WorkspaceGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Get workspace details.
    """

    return 200, workspace_service.get(user=request.authenticated_user, uid=workspace_id)


@workspace_router.patch(
    "/{workspace_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: WorkspaceGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
    exclude_unset=True,
)
@transaction.atomic
def update_workspace(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    data: WorkspacePatchBody,
):
    """
    Update a workspace owned by the authenticated user.
    """

    return 200, workspace_service.update(
        user=request.authenticated_user, uid=workspace_id, data=data
    )


@workspace_router.delete(
    "/{workspace_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: None,
        401: str,
        403: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Delete a workspace owned by the authenticated user.
    """

    return 204, workspace_service.delete(
        user=request.authenticated_user, uid=workspace_id
    )


@workspace_router.post(
    "/{workspace_id}/transfer",
    auth=[session_auth, bearer_auth],
    response={
        201: str,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def transfer_workspace(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    data: WorkspaceTransferBody,
):
    """
    Transfer a workspace owned by the authenticated user to another HydroServer user.
    """

    return 201, workspace_service.transfer(
        user=request.authenticated_user, uid=workspace_id, data=data
    )


@workspace_router.put(
    "/{workspace_id}/transfer",
    auth=[session_auth, bearer_auth],
    response={
        200: str,
        400: str,
        401: str,
        403: str,
    },
    by_alias=True,
)
@transaction.atomic
def accept_workspace_transfer(
    request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]
):
    """
    Accept a pending workspace transfer.
    """

    return 200, workspace_service.accept_transfer(
        user=request.authenticated_user, uid=workspace_id
    )


@workspace_router.delete(
    "/{workspace_id}/transfer",
    auth=[session_auth, bearer_auth],
    response={
        200: str,
        400: str,
        401: str,
        403: str,
    },
    by_alias=True,
)
@transaction.atomic
def reject_workspace_transfer(
    request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]
):
    """
    Reject a pending workspace transfer.
    """

    return 200, workspace_service.reject_transfer(
        user=request.authenticated_user, uid=workspace_id
    )
