# import os
# import uuid
# import boto3
# from ninja import File, Path
# from ninja.files import UploadedFile
# from ninja.errors import HttpError
# from typing import List
# from uuid import UUID
# from botocore.exceptions import ClientError
# from core.router import DataManagementRouter
# from core.endpoints.thing.utils import get_thing_by_id, check_thing_by_id
# from core.models import Photo
# from .schemas import PhotoGetResponse
# from .utils import build_photo_response
# from hydroserver.settings import PROXY_BASE_URL, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
#
#
# router = DataManagementRouter(tags=['Photos'])
#
#
# @router.dm_list('', response=PhotoGetResponse)
# def get_photos(request, thing_id: UUID = Path(...)):
#     """
#     Get a list of Photos
#
#     This endpoint returns a list of Photos for a Thing owned by the authenticated user if there is one.
#     """
#
#     thing = get_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         raise_http_errors=True,
#         prefetch_photos=True
#     )
#
#     return 200, [
#         build_photo_response(photo) for photo in thing.photos.all()
#     ]
#
#
# @router.dm_get('{photo_id}', response=PhotoGetResponse)
# def get_photo(request, thing_id: UUID = Path(...), photo_id: UUID = Path(...)):
#     """
#     Get a Photo for a Thing
#
#     This endpoint returns a specific Photo for a Thing owned by the authenticated user if there is one.
#     """
#
#     thing = get_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         raise_http_errors=True,
#         prefetch_photos=True
#     )
#
#     photo = next(iter([photo for photo in thing.photos.all() if photo.id == photo_id]))
#
#     if not photo:
#         raise HttpError(404, 'Photo with the given ID was not found.')
#
#     return 200, build_photo_response(photo)
#
#
# @router.dm_post('', response=List[PhotoGetResponse])
# def upload_photos(request, thing_id: UUID = Path(...), files: List[UploadedFile] = File(...)):
#     """
#     Upload Photos for a Thing
#
#     This endpoint accepts one or more files and stores them for a Thing owned by the authenticated user.
#     """
#
#     check_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         require_ownership=True,
#         raise_http_errors=True,
#     )
#
#     s3 = boto3.client(
#         's3',
#         region_name='us-east-1',
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#     )
#
#     for file in files:
#         base, extension = os.path.splitext(file.name)
#         file_name = f'photos/{str(thing_id)}/{uuid.uuid4()}{extension}'
#         file_link = f'{PROXY_BASE_URL}/{file_name}'
#         try:
#             s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
#         except ClientError as e:
#             print(f"Error uploading {file_name} to S3: {e}")
#             continue
#
#         photo = Photo(thing_id=str(thing_id), file_path='/', link=file_link)
#         photo.save()
#
#     thing = get_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         raise_http_errors=True,
#         prefetch_photos=True
#     )
#
#     return 201, [
#         build_photo_response(photo) for photo in thing.photos.all()
#     ]
#
#
# @router.dm_delete('{photo_id}')
# def delete_photo(request, thing_id: UUID = Path(...), photo_id: UUID = Path(...)):
#     """
#     Delete a Photo for a Thing
#
#     This endpoint deletes a specific Photo for a Thing owned by the authenticated user.
#     """
#
#     check_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         require_ownership=True,
#         raise_http_errors=True,
#     )
#
#     try:
#         photo = Photo.objects.get(id=photo_id)
#         photo.delete()
#     except Photo.DoesNotExist:
#         raise HttpError(404, 'Photo with the given ID was not found.')
#
#     return 204, None
