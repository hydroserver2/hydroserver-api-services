# from django.http import JsonResponse
#
# from ninja import Router
# import boto3
# import uuid
# import os
# from botocore.exceptions import ClientError
#
# from hydroserver.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, PROXY_BASE_URL
# from core.models import Photo, Thing
# from core.utils.thing import photo_to_dict
# from core.utils.authentication import jwt_auth, thing_ownership_required
#
# router = Router(tags=['Photos'])
#
# @router.post('/{thing_id}', auth=jwt_auth)
# @thing_ownership_required
# def update_thing_photos(request, thing_id):
#     try:
#         s3 = boto3.client(
#             's3',
#             region_name='us-east-1',
#             aws_access_key_id=AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#         )
#
#         # First delete specified photos if there are any
#         for photo_id in request.POST.getlist('photosToDelete', []):
#             try:
#                 photo = Photo.objects.get(id=photo_id)
#                 photo.delete()
#             except Photo.DoesNotExist:
#                 print(f"Photo {photo_id} does not exist")
#                 continue
#
#         # Add new photos if there are any
#         photos_list = []
#         for file in request.FILES.getlist('photos'):
#             base, extension = os.path.splitext(file.name)
#             file_name = f"photos/{request.thing.id}/{uuid.uuid4()}{extension}"
#             file_link = f"{PROXY_BASE_URL}/{file_name}"
#
#             # Upload the photo to S3 bucket
#             try:
#                 s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
#             except ClientError as e:
#                 print(f"Error uploading {file_name} to S3: {e}")
#                 continue
#
#             # Create a new photo in the database
#             photo = Photo(thing=request.thing, file_path='/', link=file_link)
#             photo.save()
#             photos_list.append(photo_to_dict(photo))
#
#         return JsonResponse([photo_to_dict(photo) for photo in request.thing.photos.all()],
#                             status=200, safe=False)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)
#
#
# @router.get('/{thing_id}')
# def get_thing_photos(request, thing_id):
#     try:
#         thing = Thing.objects.get(id=thing_id)
#         return JsonResponse([photo_to_dict(photo) for photo in thing.photos.all()], status=200, safe=False)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)