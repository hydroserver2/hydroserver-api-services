import uuid
from ninja import Router, Path
from hydroserver.security import basic_auth, session_auth
from iam.schemas import CollaboratorPostBody


role_router = Router(tags=["Roles"])


@role_router.get(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def get_workspaces(request, workspace_id: Path[uuid.UUID]):
    pass


@role_router.get(
    "{role_id}",
    auth=[session_auth, basic_auth],
    response={
        200: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def get_role(request, workspace_id: Path[uuid.UUID], role_id: Path[uuid.UUID]):
    pass


@role_router.get(
    "{role_id}/collaborators",
    auth=[session_auth, basic_auth],
    response={
        200: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def get_collaborators(request, workspace_id: Path[uuid.UUID], role_id: Path[uuid.UUID]):
    pass


@role_router.post(
    "{role_id}/collaborators",
    auth=[session_auth, basic_auth],
    response={
        201: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def add_collaborator(request, workspace_id: Path[uuid.UUID], role_id: Path[uuid.UUID], body: CollaboratorPostBody):
    pass



