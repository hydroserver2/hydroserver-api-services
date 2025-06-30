import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from iam.schemas import (
    CollaboratorGetResponse,
    CollaboratorQueryParameters,
    CollaboratorPostBody,
    CollaboratorDeleteBody,
)
from iam.services import CollaboratorService

collaborator_router = Router(tags=["Collaborators"])
collaborator_service = CollaboratorService()


@collaborator_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[CollaboratorGetResponse],
        401: str,
        403: str,
    },
    by_alias=True,
)
def get_collaborators(
        request: HydroServerHttpRequest,
        response: HttpResponse,
        workspace_id: Path[uuid.UUID],
        query: Query[CollaboratorQueryParameters],
):
    """
    Get all collaborators associated with a workspace.
    """

    return 200, collaborator_service.list(
        principal=request.principal,
        workspace_id=workspace_id,
        response=response,
        page=query.page,
        page_size=query.page_size,
        ordering=query.ordering,
        filtering=query.dict(exclude_unset=True),
    )


@collaborator_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: CollaboratorGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def add_collaborator(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    data: CollaboratorPostBody,
):
    """
    Add a collaborator to a workspace.
    """

    return 201, collaborator_service.create(
        principal=request.principal,
        workspace_id=workspace_id,
        data=data,
    )


@collaborator_router.put(
    "",
    auth=[session_auth, bearer_auth],
    response={
        200: CollaboratorGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def edit_collaborator_role(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    data: CollaboratorPostBody,
):
    """
    Edit a collaborator's role in a workspace.
    """

    return 200, collaborator_service.update(
        principal=request.principal,
        workspace_id=workspace_id,
        data=data,
    )


@collaborator_router.delete(
    "",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def remove_collaborator(
    request: HydroServerHttpRequest,
    workspace_id: Path[uuid.UUID],
    data: CollaboratorDeleteBody,
):
    """
    Remove a collaborator from a workspace.
    """

    return 204, collaborator_service.delete(
        principal=request.principal,
        workspace_id=workspace_id,
        data=data,
    )
