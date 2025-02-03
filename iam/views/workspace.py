import uuid
from ninja import Router, Path
from hydroserver.security import basic_auth, session_auth


workspace_router = Router(tags=["Workspaces"])


@workspace_router.get(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: str,
        401: str,
    },
    by_alias=True
)
def get_workspaces(request):
    pass


@workspace_router.post(
    "",
    auth=[session_auth, basic_auth],
    response={
        201: str,
        401: str,
    },
    by_alias=True
)
def create_workspace(request):
    pass


@workspace_router.get(
    "/{workspace_id}",
    auth=[session_auth, basic_auth],
    response={
        200: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def get_workspace(request, workspace_id: Path[uuid.UUID]):
    pass


@workspace_router.patch(
    "/{workspace_id}",
    auth=[session_auth, basic_auth],
    response={
        203: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def update_workspace(request, workspace_id: Path[uuid.UUID]):
    pass


@workspace_router.delete(
    "/{workspace_id}",
    auth=[session_auth, basic_auth],
    response={
        204: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def delete_workspace(request, workspace_id: Path[uuid.UUID]):
    pass


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
def transfer_workspace(request, workspace_id: Path[uuid.UUID]):
    pass


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
def accept_workspace(request, workspace_id: Path[uuid.UUID]):
    pass
