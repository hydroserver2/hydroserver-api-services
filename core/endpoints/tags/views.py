from uuid import UUID
from ninja import Path
from ninja.errors import HttpError
from django.db import transaction, IntegrityError
from core.models import Tag
from core.router import DataManagementRouter
from core.endpoints.tags.schemas import TagFields, TagGetResponse, TagPostBody, TagPatchBody
from core.endpoints.thing.utils import get_thing_by_id, check_thing_by_id
from core.endpoints.tags.utils import build_tag_response


router = DataManagementRouter(tags=['Things'])


@router.dm_list('', response=TagGetResponse)
def get_tags(request, thing_id: UUID = Path(...)):
    """
    Get a list of Tags

    This endpoint returns a list of Tags for a Thing owned by the authenticated user if there is one.
    """

    thing = get_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        raise_http_errors=True,
        prefetch_tags=True
    )

    return 200, [
        build_tag_response(tag) for tag in thing.tags.all()
    ]


@router.dm_get('{tag_id}', response=TagGetResponse)
def get_tag(request, thing_id: UUID = Path(...), tag_id: UUID = Path(...)):
    """
    Get a Tag for a Thing

    This endpoint returns a specific Tag for a Thing owned by the authenticated user if there is one.
    """

    thing = get_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        raise_http_errors=True,
        prefetch_tags=True
    )

    tag = next(iter([tag for tag in thing.tags.all() if tag.id == tag_id]), None)

    if not tag:
        raise HttpError(404, 'Tag with the given ID was not found.')

    return 200, build_tag_response(tag)


@router.dm_post('', response=TagGetResponse)
@transaction.atomic
def create_tag(request, data: TagPostBody, thing_id: UUID = Path(...)):
    """
    Create a Tag for a Thing

    This endpoint creates a new Tag for a Thing owned by the authenticated user.
    """

    check_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        raise_http_errors=True
    )

    tag = Tag.objects.create(
        thing_id=thing_id,
        **data.dict(include=set(TagFields.__fields__.keys()))
    )

    return 201, build_tag_response(tag)


@router.dm_patch('{tag_id}', response=TagGetResponse)
@transaction.atomic
def update_tag(request, data: TagPatchBody, thing_id: UUID = Path(...), tag_id: UUID = Path(...)):
    """
    Update a Tag for a Thing

    This endpoint updates an existing Tag for a Thing owned by the authenticated user.
    """

    thing = get_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        raise_http_errors=True
    )

    tag = next(iter([tag for tag in thing.tags.all() if tag.id == tag_id]), None)

    if not tag:
        raise HttpError(404, 'Tag with the given ID was not found.')

    tag_data = data.dict(include=set(TagFields.__fields__.keys()), exclude_unset=True)

    for field, value in tag_data.items():
        setattr(tag, field, value)

    tag.save()

    return 203, build_tag_response(tag)


@router.dm_delete('{tag_id}')
def delete_tag(request, thing_id: UUID = Path(...), tag_id: UUID = Path(...)):
    """
    Delete a Tag

    This endpoint will delete an existing Tag if the authenticated user is the primary owner of the
    Thing.
    """

    thing = get_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        raise_http_errors=True
    )

    tag = next(iter([tag for tag in thing.tags.all() if tag.id == tag_id]), None)

    if not tag:
        raise HttpError(404, 'Tag with the given ID was not found.')

    try:
        tag.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
