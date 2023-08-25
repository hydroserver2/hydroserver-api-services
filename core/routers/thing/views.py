import os
import uuid
import boto3
from ninja import Router, File
from ninja.files import UploadedFile
from django.http import HttpRequest
from django.db import transaction
from botocore.exceptions import ClientError
from accounts.auth import BasicAuth, JWTAuth
from core.routers.thing.schemas import *
from core.routers.thing.utils import transfer_sensor_ownership, build_things_query, query_things, photo_to_dict, \
     transfer_properties_ownership, transfer_processing_level_ownership, transfer_unit_ownership
from sites.models import Thing, ThingAssociation, Location, Photo
from accounts.models import CustomUser
from hydroserver import settings



router = Router(tags=['Things'])


@router.get(
    '/things',
    auth=[JWTAuth()],
    response={200: List[ThingGetResponse]}
)
def get_things(
        request: HttpRequest,
        # params: ThingQueryParams = Query(...)
):
    """"""

    things = query_things(
        authenticated_user=getattr(request, 'authenticated_user', None)
    )

    return 200, things


@router.get(
    '/things/{thing_id}',
    response={200: ThingGetResponse, 404: None}
)
def get_thing(
        request: HttpRequest,
        thing_id: UUID
):
    """"""

    things = query_things(
        thing_id=str(thing_id),
        authenticated_user=getattr(request, 'authenticated_user', None)
    )

    if not things:
        return 404, None

    return 200, things[0]


@router.get(
    '/things/{thing_id}/photos',
    response={200: List[ThingPhoto], 404: None}
)
def get_thing_photos(
        request: HttpRequest,
        thing_id: UUID
):
    """"""

    thing_query = build_things_query(
        thing_id=thing_id,
        authenticated_user=getattr(request, 'authenticated_user', None)
    )

    thing = thing_query.first()

    if not thing:
        return 404, None

    return 200, [photo_to_dict(photo) for photo in thing.photos.all()]


@router.post(
    '/things',
    auth=[BasicAuth()],
    response={201: ThingGetResponse}
)
@transaction.atomic
def create_thing(
        request: HttpRequest,
        data: ThingPostBody
):
    thing = Thing.objects.create(
        name=data.name,
        description=data.description,
        sampling_feature_type=data.sampling_feature_type,
        sampling_feature_code=data.sampling_feature_code,
        site_type=data.site_type
    )

    Location.objects.create(
        name='Location for ' + thing.name,
        description='location',
        encoding_type="application/geo+json",
        latitude=data.latitude, longitude=data.longitude, elevation=data.elevation,
        state=data.state,
        county=data.county,
        thing=thing
    )

    ThingAssociation.objects.create(
        thing=thing,
        person=getattr(request, 'authenticated_user'),
        owns_thing=True,
        is_primary_owner=True
    )

    things = query_things(thing_id=thing.id, authenticated_user=getattr(request, 'authenticated_user', None))

    return 201, next(iter(things), None)


@router.post(
    '/things/{thing_id}/photos',
    auth=[BasicAuth()],
    response={201: List[ThingPhoto], 403: None}
)
@transaction.atomic
def update_thing_photos(
        request: HttpRequest,
        thing_id: UUID,
        data: ThingPhotoPostBody,
        files: List[UploadedFile] = File(...)
):
    """"""

    thing_query = build_things_query(
        thing_id=thing_id,
        authenticated_user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    thing = thing_query.first()

    if not thing:
        return 403, None

    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    for photo_id in data.photosToDelete:
        try:
            photo = Photo.objects.get(id=photo_id)
            photo.delete()
        except Photo.DoesNotExist:
            print(f"Photo {photo_id} does not exist")
            continue

    photos_list = []
    for file in files:
        base, extension = os.path.splitext(file.name)
        file_name = f"{str(thing_id)}/{uuid.uuid4()}{extension}"
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

        # Upload the photo to S3 bucket
        try:
            s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_name)
        except ClientError as e:
            print(f"Error uploading {file_name} to S3: {e}")
            continue

        # Create a new photo in the database
        photo = Photo(thing=thing, url=file_url)
        photo.save()
        photos_list.append(photo_to_dict(photo))

    return 200, [photo_to_dict(photo) for photo in thing.photos.all()]


@router.patch(
    '/things/{thing_id}',
    auth=[BasicAuth()],
    response={203: ThingGetResponse, 403: None}
)
@transaction.atomic
def update_thing(
        request: HttpRequest,
        thing_id: UUID,
        data: ThingPatchBody
):
    """"""

    thing_query = build_things_query(
        thing_id=thing_id,
        authenticated_user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    thing = thing_query.first()

    if not thing:
        return 403, None

    location = Location.objects.get(thing=thing)

    data_dict = data.dict(exclude_unset=True)

    if 'name' in data_dict:
        thing.name = data_dict['name']
        location.name = 'Location for ' + data_dict['name']
    if 'description' in data_dict:
        thing.description = data_dict['description']
    if 'sampling_feature_type' in data_dict:
        thing.sampling_feature_type = data_dict['sampling_feature_type']
    if 'sampling_feature_code' in data_dict:
        thing.sampling_feature_code = data_dict['sampling_feature_code']
    if 'site_type' in data_dict:
        thing.site_type = data_dict['site_type']

    if 'latitude' in data_dict:
        location.latitude = data['latitude']
    if 'longitude' in data_dict:
        location.longitude = data['longitude']
    if 'elevation' in data_dict:
        location.elevation = data['elevation']
    if 'city' in data_dict:
        location.city = data['city']
    if 'state' in data_dict:
        location.state = data['state']
    if 'county' in data_dict:
        location.county = data['county']

    thing.save()
    location.save()

    things = query_things(thing_id=thing_id, authenticated_user=getattr(request, 'authenticated_user', None))

    return 201, next(iter(things), None)


@router.patch(
    '/things/{thing_id}/ownership',
    auth=[BasicAuth()],
    response={203: ThingGetResponse, 403: str, 404: str}
)
@transaction.atomic
def update_thing_ownership(
        request: HttpRequest,
        thing_id: UUID,
        data: ThingOwnershipPatchBody
):
    """"""

    thing_query = build_things_query(
        thing_id=thing_id,
        authenticated_user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    thing = thing_query.first()

    if not thing:
        return 403, None

    authenticated_user = getattr(request, 'authenticated_user', None)

    try:
        user = CustomUser.objects.get(email=data.email)
    except CustomUser.DoesNotExist:
        return 404, 'Specified user not found.'

    current_user_association = ThingAssociation.objects.get(
        thing=thing,
        person=authenticated_user
    )

    if authenticated_user == user and current_user_association.is_primary_owner:
        return 403, 'Primary owner cannot edit their own ownership.'
    if not current_user_association.is_primary_owner and user != authenticated_user:
        return 403, 'Only the primary owner can modify other users\' ownership.'

    thing_association, created = ThingAssociation.objects.get_or_create(thing=thing, person=user)

    if data.transfer_primary:
        if not current_user_association.is_primary_owner:
            return 403, 'Only primary owner can transfer primary ownership.'
        datastreams = thing.datastreams.all()
        for datastream in datastreams:
            transfer_properties_ownership(datastream, user, authenticated_user)
            transfer_processing_level_ownership(datastream, user, authenticated_user)
            transfer_unit_ownership(datastream, user, authenticated_user)
            transfer_sensor_ownership(datastream, user, authenticated_user)
        current_user_association.is_primary_owner = False
        current_user_association.save()
        thing_association.is_primary_owner = True
        thing_association.owns_thing = True
    elif data.remove_owner:
        if thing_association.is_primary_owner:
            return 400, 'Cannot remove primary owner.'
        thing_association.delete()
        things = query_things(thing_id=thing_id, authenticated_user=authenticated_user)
        return 203, next(iter(things), None)
    elif data.make_owner:
        thing_association.owns_thing = True

    thing_association.follows_thing = False
    thing_association.save()
    things = query_things(thing_id=thing_id, authenticated_user=authenticated_user)
    return 203, next(iter(things), None)


@router.patch(
    '/things/{thing_id}/privacy',
    auth=[BasicAuth()],
    response={203: ThingGetResponse}
)
@transaction.atomic
def update_thing_privacy(
        request: HttpRequest,
        thing_id: UUID,
        data: ThingPrivacyPatchBody
):
    """"""

    thing_query = build_things_query(
        thing_id=thing_id,
        authenticated_user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    thing = thing_query.first()

    if not thing:
        return 403, None

    thing.is_private = data.is_private
    thing_associations = ThingAssociation.objects.filter(thing=thing)

    if data.is_private:
        for thing_association in thing_associations:
            if thing_association.follows_thing:
                thing_association.delete()

    thing.save()

    things = query_things(thing_id=thing_id, authenticated_user=getattr(request, 'authenticated_user', None))
    return 200, next(iter(things), None)


@router.patch(
    '/things/{thing_id}/followership',
    auth=[BasicAuth()],
    response={203: ThingGetResponse, 400: str}
)
def update_thing_followership(
        request: HttpRequest,
        thing_id: UUID
):
    """"""

    thing = Thing.objects.get(id=thing_id)
    authenticated_user = getattr(request, 'authenticated_user')

    if authenticated_user.thing_associations.filter(thing=thing, owns_thing=True).exists():
        return 400, 'Owners cannot update follow status'

    thing_association, created = ThingAssociation.objects.get_or_create(thing=thing, person=authenticated_user)

    if thing_association.follows_thing:
        thing_association.delete()
    else:
        thing_association.follows_thing = True
        thing_association.save()

    things = query_things(thing_id=thing_id, authenticated_user=getattr(request, 'authenticated_user', None))
    return 200, next(iter(things), None)


@router.delete(
    '/things/{thing_id}',
    auth=[BasicAuth()],
    response={200: None, 500: None}
)
def delete_thing(
        request: HttpRequest,
        thing_id: UUID
):
    """"""

    thing_query = build_things_query(
        thing_id=thing_id,
        authenticated_user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    thing = thing_query.first()

    if not thing:
        return 403, None

    try:
        thing.delete()
    except Exception as e:
        return 500, str(e)

    return 200, 'Site deleted successfully.'
