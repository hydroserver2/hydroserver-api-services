import uuid
from ninja import Router, Path
from hydroserver.http import HydroServerHttpRequest
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from iam.services import RoleService
from iam.schemas import RoleGetResponse

role_router = Router(tags=["Roles"])
role_service = RoleService()


@role_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[RoleGetResponse],
        401: str,
        403: str,
    },
    by_alias=True,
)
def get_roles(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Get all assignable roles for the given workspace.
    """

    return 200, role_service.list(
        principal=request.principal, workspace_id=workspace_id
    )


@role_router.get(
    "{role_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: RoleGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
)
def get_role(request, workspace_id: Path[uuid.UUID], role_id: Path[uuid.UUID]):
    """
    Get a role that can be used within a workspace.
    """

    return 200, role_service.get(
        principal=request.principal, uid=role_id, workspace_id=workspace_id
    )
