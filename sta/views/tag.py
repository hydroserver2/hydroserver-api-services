import uuid
from ninja import Router, Path
from hydroserver.security import basic_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import TagGetResponse, TagPostBody, TagDeleteBody
from sta.services import ThingService

tag_router = Router(tags=["Tags"])
thing_service = ThingService()


@tag_router.get(
    "",
    auth=[session_auth, basic_auth, anonymous_auth],
    response={
        200: list[TagGetResponse],
        401: str,
        403: str,
    },
    by_alias=True
)
def get_tags(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Get all tags associated with a Thing.
    """

    return 200, thing_service.get_tags(
        user=request.authenticated_user,
        uid=thing_id,
    )


@tag_router.post(
    "",
    auth=[session_auth, basic_auth],
    response={
        201: TagGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def add_tag(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: TagPostBody):
    """
    Add a tag to a Thing.
    """

    return 201, thing_service.add_tag(
        user=request.authenticated_user,
        uid=thing_id,
        data=data,
    )


@tag_router.put(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: TagGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def edit_tag(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: TagPostBody):
    """
    Edit a tag of a Thing.
    """

    return 200, thing_service.update_tag(
        user=request.authenticated_user,
        uid=thing_id,
        data=data,
    )


@tag_router.delete(
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
def remove_tag(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: TagDeleteBody):
    """
    Remove a tag from a Thing.
    """

    return 204, thing_service.remove_tag(
        user=request.authenticated_user,
        uid=thing_id,
        data=data,
    )
