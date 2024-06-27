from uuid import UUID
from ninja import Path
from ninja.errors import HttpError
from django.db import transaction, IntegrityError
from core.models import Thing, Tag
from core.router import DataManagementRouter
from core.schemas.thing import TagFields, TagGetResponse, TagPostBody, TagPatchBody


thing_tag_router = DataManagementRouter(tags=['Tags'])
user_tag_router = DataManagementRouter(tags=['Tags'])


@user_tag_router.dm_list('', response=TagGetResponse)
def get_tags(request):
    """
    Get a list of Tags associated with a user

    This endpoint returns a list of tags used by the authenticated user.
    """

    thing_query = Thing.objects.prefetch_associates().prefetch_related('tags')
    thing_query = thing_query.owner(user=request.authenticated_user)

    user_tags = [tag for tags in [
        thing.tags.all() for thing in thing_query.all()
    ] for tag in tags]

    return 200, [
        TagGetResponse.serialize(tag) for tag in user_tags
    ]


@thing_tag_router.dm_list('', response=TagGetResponse)
def get_thing_tags(request, thing_id: UUID = Path(...)):
    """
    Get a list of Tags for a Thing

    This endpoint returns a list of tags for a thing owned by the authenticated user if there is one.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True,
        prefetch=['tags']
    )

    return 200, [
        TagGetResponse.serialize(tag) for tag in thing.tags.all()
    ]


@thing_tag_router.dm_get('{tag_id}', response=TagGetResponse)
def get_tag(request, thing_id: UUID = Path(...), tag_id: UUID = Path(...)):
    """
    Get a Tag for a Thing

    This endpoint returns a specific tag for a thing owned by the authenticated user if there is one.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True,
        prefetch=['tags']
    )

    tag = next(iter([tag for tag in thing.tags.all() if tag.id == tag_id]), None)

    if not tag:
        raise HttpError(404, 'Tag with the given ID was not found.')

    return 200, TagGetResponse.serialize(tag)


@thing_tag_router.dm_post('', response=TagGetResponse)
@transaction.atomic
def create_tag(request, data: TagPostBody, thing_id: UUID = Path(...)):
    """
    Create a Tag for a Thing

    This endpoint creates a new tag for a thing owned by the authenticated user.
    """

    Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True,
        fetch=False
    )

    tag = Tag.objects.create(
        thing_id=thing_id,
        **data.dict(include=set(TagFields.model_fields.keys()))
    )

    return 201, TagGetResponse.serialize(tag)


@thing_tag_router.dm_patch('{tag_id}', response=TagGetResponse)
@transaction.atomic
def update_tag(request, data: TagPatchBody, thing_id: UUID = Path(...), tag_id: UUID = Path(...)):
    """
    Update a Tag for a Thing

    This endpoint updates an existing tag for a thing owned by the authenticated user.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True,
        prefetch=['tags']
    )

    tag = next(iter([tag for tag in thing.tags.all() if tag.id == tag_id]), None)

    if not tag:
        raise HttpError(404, 'Tag with the given ID was not found.')

    tag_data = data.dict(include=set(TagFields.model_fields.keys()), exclude_unset=True)

    for field, value in tag_data.items():
        setattr(tag, field, value)

    tag.save()

    return 203, TagGetResponse.serialize(tag)


@thing_tag_router.dm_delete('{tag_id}')
def delete_tag(request, thing_id: UUID = Path(...), tag_id: UUID = Path(...)):
    """
    Delete a Tag

    This endpoint will delete an existing tag if the authenticated user is the primary owner of the
    thing.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True,
        prefetch=['tags']
    )

    tag = next(iter([tag for tag in thing.tags.all() if tag.id == tag_id]), None)

    if not tag:
        raise HttpError(404, 'Tag with the given ID was not found.')

    try:
        tag.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
