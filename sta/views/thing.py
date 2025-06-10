import uuid
from ninja import Router, Path, Query
from django.db import transaction
from django.http import HttpResponse
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import (
    ThingCollectionResponse,
    ThingGetResponse,
    ThingPostBody,
    ThingPatchBody,
    ThingQueryParameters,
)
from sta.services import ThingService

thing_router = Router(tags=["Things"])
thing_service = ThingService()


@thing_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[ThingCollectionResponse],
        401: str,
    },
    by_alias=True,
)
def get_things(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[ThingQueryParameters],
):
    """
    Get public Things and Things associated with the authenticated user.
    """

    return 200, thing_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        ordering=query.ordering,
        filtering={
            field: getattr(query, field)
            for field in ThingQueryParameters.__annotations__
        },
    )


@thing_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
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

    return 201, thing_service.create(principal=request.principal, data=data)


@thing_router.get(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
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

    return 200, thing_service.get(principal=request.principal, uid=thing_id)


@thing_router.patch(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
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
        principal=request.principal, uid=thing_id, data=data
    )


@thing_router.delete(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
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

    return 204, thing_service.delete(principal=request.principal, uid=thing_id)
