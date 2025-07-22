import uuid
from typing import Optional
from ninja import Router, Path, Query, File
from ninja.files import UploadedFile
from django.db import transaction
from django.http import HttpResponse
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from api.schemas import VocabularyQueryParameters
from sta.schemas import (
    ThingSummaryResponse,
    ThingDetailResponse,
    ThingPostBody,
    ThingPatchBody,
    ThingQueryParameters,
    TagGetResponse,
    TagPostBody,
    TagDeleteBody,
    PhotoGetResponse,
    PhotoDeleteBody,
)
from sta.services import ThingService
from etl.views.hydroshare_archival import hydroshare_archival_router

thing_router = Router(tags=["Things"])
thing_service = ThingService()


@thing_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[ThingSummaryResponse] | list[ThingDetailResponse],
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
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
        expand_related=query.expand_related,
    )


@thing_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: ThingSummaryResponse | ThingDetailResponse,
        400: str,
        401: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_thing(
    request: HydroServerHttpRequest,
    data: ThingPostBody,
    expand_related: Optional[bool] = None,
):
    """
    Create a new Thing.
    """

    return 201, thing_service.create(
        principal=request.principal, data=data, expand_related=expand_related
    )


@thing_router.get(
    "/tags/keys",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: dict[str, list[str]],
        401: str,
    },
)
def get_tag_keys(
    request: HydroServerHttpRequest,
    workspace_id: Optional[uuid.UUID] = None,
    thing_id: Optional[uuid.UUID] = None,
):
    """
    Get all existing unique tag keys.
    """

    return 200, thing_service.get_tag_keys(
        principal=request.principal,
        workspace_id=workspace_id,
        thing_id=thing_id,
    )


@thing_router.get("/site-types", response={200: list[str]}, by_alias=True)
def get_site_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get site types.
    """

    return 200, thing_service.list_site_types(
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@thing_router.get("/sampling-feature-types", response={200: list[str]}, by_alias=True)
def get_sampling_feature_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get sampling feature types.
    """

    return 200, thing_service.list_sampling_feature_types(
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@thing_router.get(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: ThingSummaryResponse | ThingDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_thing(
    request: HydroServerHttpRequest,
    thing_id: Path[uuid.UUID],
    expand_related: Optional[bool] = None,
):
    """
    Get a Thing.
    """

    return 200, thing_service.get(
        principal=request.principal, uid=thing_id, expand_related=expand_related
    )


@thing_router.patch(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: ThingSummaryResponse | ThingDetailResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_thing(
    request: HydroServerHttpRequest,
    thing_id: Path[uuid.UUID],
    data: ThingPatchBody,
    expand_related: Optional[bool] = None,
):
    """
    Update a Thing.
    """

    return 200, thing_service.update(
        principal=request.principal,
        uid=thing_id,
        data=data,
        expand_related=expand_related,
    )


@thing_router.delete(
    "/{thing_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: None,
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


@thing_router.get(
    "/{thing_id}/tags",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[TagGetResponse],
        401: str,
        403: str,
    },
    by_alias=True,
)
def get_tags(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Get all tags associated with a Thing.
    """

    return 200, thing_service.get_tags(
        principal=request.principal,
        uid=thing_id,
    )


@thing_router.post(
    "/{thing_id}/tags",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: TagGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
def add_tag(
    request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: TagPostBody
):
    """
    Add a tag to a Thing.
    """

    return 201, thing_service.add_tag(
        principal=request.principal,
        uid=thing_id,
        data=data,
    )


@thing_router.put(
    "/{thing_id}/tags",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: TagGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
def edit_tag(
    request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: TagPostBody
):
    """
    Edit a tag of a Thing.
    """

    return 200, thing_service.update_tag(
        principal=request.principal,
        uid=thing_id,
        data=data,
    )


@thing_router.delete(
    "/{thing_id}/tags",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: None,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
def remove_tag(
    request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: TagDeleteBody
):
    """
    Remove a tag from a Thing.
    """

    return 204, thing_service.remove_tag(
        principal=request.principal,
        uid=thing_id,
        data=data,
    )


@thing_router.get(
    "/{thing_id}/photos",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[PhotoGetResponse],
        401: str,
        403: str,
    },
    by_alias=True,
)
def get_photos(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Get all photos associated with a Thing.
    """

    return 200, thing_service.get_photos(
        principal=request.principal,
        uid=thing_id,
    )


@thing_router.post(
    "/{thing_id}/photos",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: PhotoGetResponse,
        400: str,
        401: str,
        403: str,
        413: str,
        422: str,
    },
    by_alias=True,
)
def add_photo(
    request: HydroServerHttpRequest,
    thing_id: Path[uuid.UUID],
    file: UploadedFile = File(...),
):
    """
    Add a photo to a thing.
    """

    return 201, thing_service.add_photo(
        principal=request.principal, uid=thing_id, file=file
    )


@thing_router.delete(
    "/{thing_id}/photos",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: None,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
def remove_photo(
    request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: PhotoDeleteBody
):
    """
    Remove a photo from a thing.
    """

    return 204, thing_service.remove_photo(
        principal=request.principal,
        uid=thing_id,
        data=data,
    )


thing_router.add_router("{thing_id}/archive", hydroshare_archival_router)
