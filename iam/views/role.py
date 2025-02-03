import uuid
from ninja import Router
from hydroserver.security import basic_auth, session_auth


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
def get_workspaces(request, workspace_id: uuid.UUID):
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
def get_role(request, workspace_id: uuid.UUID, role_id: uuid.UUID):
    pass
