import os
import uuid
import boto3
from ninja import File, Path
from ninja.files import UploadedFile
from ninja.errors import HttpError
from typing import List
from uuid import UUID
from botocore.exceptions import ClientError
from core.router import DataManagementRouter
from core.models import Thing, Photo
from core.schemas.thing import PhotoGetResponse
from hydroserver.settings import PROXY_BASE_URL, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


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

    # s3 = boto3.client(
    #     's3',
    #     region_name='us-east-1',
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    # )

    for file in files:
        photo = Photo.objects.create(
            thing_id=thing_id,
            file_path='TEST',
            link='TEST'
        )
        photo.file.save(file.name, file)

        # base, extension = os.path.splitext(file.name)
        # file_name = f'photos/{str(thing_id)}/{uuid.uuid4()}{extension}'
        # file_link = f'{PROXY_BASE_URL}/{file_name}'
        # try:
        #     s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
        # except ClientError as e:
        #     print(f"Error uploading {file_name} to S3: {e}")
        #     continue
        #
        # photo = Photo(thing_id=str(thing_id), file_path='/', link=file_link)
        # photo.save()

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
        photo.delete()
    except Photo.DoesNotExist:
        raise HttpError(404, 'Photo with the given ID was not found.')

    return 204, None
