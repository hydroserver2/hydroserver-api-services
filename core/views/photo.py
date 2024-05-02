import os
from ninja import File, Path
from ninja.files import UploadedFile
from ninja.errors import HttpError
from typing import List
from uuid import UUID
from core.router import DataManagementRouter
from core.models import Thing, Photo
from core.schemas.thing import PhotoGetResponse


router = DataManagementRouter(tags=['Photos'])


@router.dm_list('', response=PhotoGetResponse)
def get_photos(request, thing_id: UUID = Path(...)):
    """
    Get a list of Photos

    This endpoint returns a list of Photos for a Thing owned by the authenticated user if there is one.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True,
        prefetch=['photos']
    )

    return 200, [
        PhotoGetResponse.serialize(photo) for photo in thing.photos.all()
    ]


@router.dm_get('{photo_id}', response=PhotoGetResponse)
def get_photo(request, thing_id: UUID = Path(...), photo_id: UUID = Path(...)):
    """
    Get a Photo for a Thing

    This endpoint returns a specific Photo for a Thing owned by the authenticated user if there is one.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True,
        prefetch=['photos']
    )

    photo = next(iter([photo for photo in thing.photos.all() if photo.id == photo_id]), None)

    if not photo:
        raise HttpError(404, 'Photo with the given ID was not found.')

    return 200, PhotoGetResponse.serialize(photo)


@router.dm_post('', response=List[PhotoGetResponse])
def upload_photos(request, thing_id: UUID = Path(...), files: List[UploadedFile] = File(...)):
    """
    Upload Photos for a Thing

    This endpoint accepts one or more files and stores them for a Thing owned by the authenticated user.
    """

    Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True,
        fetch=False
    )

    for file in files:
        photo = Photo.objects.create(
            thing_id=thing_id,
        )
        photo.file_path.save(name=os.path.join(str(thing_id), file.name,), content=file)

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True,
        prefetch=['photos']
    )

    return 201, [
        PhotoGetResponse.serialize(photo) for photo in thing.photos.all()
    ]


@router.dm_delete('{photo_id}')
def delete_photo(request, thing_id: UUID = Path(...), photo_id: UUID = Path(...)):
    """
    Delete a Photo for a Thing

    This endpoint deletes a specific Photo for a Thing owned by the authenticated user.
    """

    Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True,
        fetch=False
    )

    try:
        photo = Photo.objects.get(id=photo_id)
        photo.file_path.delete()
        photo.delete()
    except Photo.DoesNotExist:
        raise HttpError(404, 'Photo with the given ID was not found.')

    return 204, None
