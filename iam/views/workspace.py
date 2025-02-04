import uuid
from ninja import Router, Path
from hydroserver.http import HydroServerHttpRequest
from hydroserver.security import basic_auth, session_auth
from iam.schemas import WorkspaceGetResponse, WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody
from iam.services import WorkspaceService


workspace_router = Router(tags=["Workspaces"])


@workspace_router.get(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: list[WorkspaceGetResponse],
        401: str,
    },
    by_alias=True
)
def get_workspaces(request: HydroServerHttpRequest, associated_only: bool = False):
    """
    Get public workspaces and workspaces associated with the authenticated user.
    """

    return 200, WorkspaceService.list(
        user=request.authenticated_user,
        associated_only=associated_only
    )


@workspace_router.post(
    "",
    auth=[session_auth, basic_auth],
    response={
        201: WorkspaceGetResponse,
        401: str,
    },
    by_alias=True
)
def create_workspace(request: HydroServerHttpRequest, data: WorkspacePostBody):
    """
    Create a new workspace owned by the authenticated user.
    """

    return 201, WorkspaceService.create(
        user=request.authenticated_user,
        data=data
    )


@workspace_router.get(
    "/{workspace_id}",
    auth=[session_auth, basic_auth],
    response={
        200: WorkspaceGetResponse,
        401: str,
        403: str,
    },
    by_alias=True
)
def get_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Get workspace details.
    """

    return 200, WorkspaceService.get(
        user=request.authenticated_user,
        uid=workspace_id
    )


@workspace_router.patch(
    "/{workspace_id}",
    auth=[session_auth, basic_auth],
    response={
        203: WorkspaceGetResponse,
        401: str,
        403: str,
    },
    by_alias=True
)
def update_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID], data: WorkspacePatchBody):
    """
    Update a workspace owned by the authenticated user.
    """

    return 203, WorkspaceService.update(
        user=request.authenticated_user,
        uid=workspace_id,
        data=data
    )


@workspace_router.delete(
    "/{workspace_id}",
    auth=[session_auth, basic_auth],
    response={
        204: None,
        401: str,
        403: str,
    },
    by_alias=True
)
def delete_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Delete a workspace owned by the authenticated user.
    """

    return 204, WorkspaceService.delete(
        user=request.authenticated_user,
        uid=workspace_id
    )


@workspace_router.post(
    "/{workspace_id}/transfer",
    auth=[session_auth, basic_auth],
    response={
        201: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def transfer_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID], data: WorkspaceTransferBody):
    """
    Transfer a workspace owned by the authenticated user to another HydroServer user.
    """

    return 201, WorkspaceService.transfer(
        user=request.authenticated_user,
        uid=workspace_id,
        data=data
    )


@workspace_router.post(
    "/{workspace_id}/transfer/accept",
    auth=[session_auth, basic_auth],
    response={
        201: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def accept_workspace(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Accept a pending workspace transfer.
    """

    return 201, WorkspaceService.accept(
        user=request.authenticated_user,
        uid=workspace_id
    )
