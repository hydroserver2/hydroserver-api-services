import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import ThingGetResponse, ThingPostBody, ThingPatchBody
from sta.services import ThingService

thing_router = Router(tags=["Things"])
thing_service = ThingService()


@thing_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[ThingGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_things(
    request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None
):
    """
    Get public Things and Things associated with the authenticated user.
    """

    return 200, thing_service.list(
        user=request.authenticated_user, workspace_id=workspace_id
    )


@thing_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: ThingGetResponse,
        400: str,
        401: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_thing(request: HydroServerHttpRequest, data: ThingPostBody):
    """
    Create a new Thing.
    """

    return 201, thing_service.create(user=request.authenticated_user, data=data)


@thing_router.get(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: ThingGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_thing(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Get a Thing.
    """

    return 200, thing_service.get(user=request.authenticated_user, uid=thing_id)


@thing_router.patch(
    "/{thing_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: ThingGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_thing(
    request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: ThingPatchBody
):
    """
    Update a Thing.
    """

    return 200, thing_service.update(
        user=request.authenticated_user, uid=thing_id, data=data
    )


@thing_router.delete(
    "/{thing_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_thing(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Delete a Thing.
    """

    return 204, thing_service.delete(user=request.authenticated_user, uid=thing_id)
