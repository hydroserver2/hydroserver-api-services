import os
import uuid
import boto3
from ninja import Router, File
from ninja.files import UploadedFile
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from accounts.auth.anonymous import anonymous_auth
from typing import List
from botocore.exceptions import ClientError
from core.routers.thing.utils import query_thing_by_id
from core.models import Photo
from .schemas import PhotoGetResponse, PhotoPostBody
from .utils import build_photo_response
from hydroserver.settings import PROXY_BASE_URL, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


router = Router(tags=['Photos'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth(), anonymous_auth],
    response={
        200: List[PhotoGetResponse],
        404: str
    },
    by_alias=True
)
def get_thing_photos(request, thing_id):
    """
    Get photos for a Thing

    This endpoint returns photo details for a Thing given a Thing ID.
    """

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id, prefetch_photos=True)

    return [
        build_photo_response(photo) for photo in thing.photos.all()
    ]


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: List[PhotoGetResponse]
    },
    by_alias=True
)
def update_thing_photos(request, thing_id, data: PhotoPostBody, files: List[UploadedFile] = File(...)):
    """"""

    thing = query_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        require_ownership=True,
        prefetch_photos=True
    )

    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    for photo_id in data.photos_to_delete:
        try:
            photo = Photo.objects.get(id=photo_id)
            photo.delete()
        except Photo.DoesNotExist:
            continue

    for file in files:
        base, extension = os.path.splitext(file.name)
        file_name = f'photos/{thing.id}/{uuid.uuid4()}{extension}'
        file_link = f'{PROXY_BASE_URL}/{file_name}'
        try:
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
        except ClientError as e:
            print(f"Error uploading {file_name} to S3: {e}")
            continue

        photo = Photo(thing=thing, file_path='/', link=file_link)
        photo.save()

    return [
        build_photo_response(photo) for photo in thing.photos.all()
    ]
