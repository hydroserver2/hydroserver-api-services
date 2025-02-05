import uuid
from ninja import Router, Path
from hydroserver.security import basic_auth, session_auth
from hydroserver.http import HydroServerHttpRequest
from iam.schemas import CollaboratorGetResponse, CollaboratorPostBody, CollaboratorDeleteBody
from iam.services import CollaboratorService


collaborator_router = Router(tags=["Collaborators"])
collaborator_service = CollaboratorService()


@collaborator_router.get(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: list[CollaboratorGetResponse],
        401: str,
        403: str,
    },
    by_alias=True
)
def get_collaborators(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID]):
    """
    Get all collaborators associated with a workspace.
    """

    return 200, collaborator_service.list(
        user=request.authenticated_user,
        workspace_id=workspace_id,
    )


@collaborator_router.post(
    "",
    auth=[session_auth, basic_auth],
    response={
        201: CollaboratorGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def add_collaborator(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID], data: CollaboratorPostBody):
    """
    Add a collaborator to a workspace.
    """

    return 201, collaborator_service.create(
        user=request.authenticated_user,
        workspace_id=workspace_id,
        data=data,
    )


@collaborator_router.put(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: CollaboratorGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def edit_collaborator_role(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID], data: CollaboratorPostBody):
    """
    Edit a collaborator's role in a workspace.
    """

    return 200, collaborator_service.update(
        user=request.authenticated_user,
        workspace_id=workspace_id,
        data=data,
    )


@collaborator_router.delete(
    "",
    auth=[session_auth, basic_auth],
    response={
        204: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def remove_collaborator(request: HydroServerHttpRequest, workspace_id: Path[uuid.UUID], data: CollaboratorDeleteBody):
    """
    Remove a collaborator from a workspace.
    """

    return 204, collaborator_service.delete(
        user=request.authenticated_user,
        workspace_id=workspace_id,
        data=data,
    )
