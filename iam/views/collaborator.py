import uuid
from ninja import Router, Path
from hydroserver.security import basic_auth, session_auth
from iam.schemas import CollaboratorPostBody


collaborator_router = Router(tags=["Collaborators"])


@collaborator_router.get(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def get_collaborators(request, workspace_id: Path[uuid.UUID]):
    pass


@collaborator_router.post(
    "",
    auth=[session_auth, basic_auth],
    response={
        201: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def add_collaborator(request, workspace_id: Path[uuid.UUID], body: CollaboratorPostBody):
    pass


@collaborator_router.delete(
    "",
    auth=[session_auth, basic_auth],
    response={
        204: str,
        401: str,
        403: str,
    },
    by_alias=True
)
def remove_collaborator(request, workspace_id: Path[uuid.UUID], body: CollaboratorPostBody):
    pass
