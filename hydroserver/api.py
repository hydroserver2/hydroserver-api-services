import copy
import uuid
from functools import wraps
from datetime import timedelta

import os
from django.contrib.auth import authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpRequest
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from ninja import Schema, NinjaAPI, Query
from ninja.security import HttpBasicAuth
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from ninja.errors import HttpError
from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID
from hydroloader import HydroLoaderConf, HydroLoaderConfFileTimestamp, HydroLoaderConfFileDatastream, \
     HydroLoaderConfSchedule, HydroLoaderConfFileAccess
from hydrothings.validators import allow_partial

from accounts.models import CustomUser, PasswordReset
from sites.models import Datastream, Sensor, ObservedProperty, Unit, ThingAssociation, Thing, Location, Observation, \
    ProcessingLevel, DataSource, DataSourceOwner, DataLoader, DataLoaderOwner, Photo
import boto3
from botocore.exceptions import ClientError
from hydroserver.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, PROXY_BASE_URL

class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            request.authenticated_user = user
            return user


api = NinjaAPI()


def jwt_auth(request):
    try:
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        request.authenticated_user = user
        return True
    except (KeyError, IndexError, InvalidToken, TokenError) as e:
        if isinstance(e, TokenError) and str(e) == 'Token is invalid or expired':
            raise HttpError(401, 'Token is invalid or expired')
        raise HttpError(401, 'Unauthorized')


def jwt_check_user(request):
    """
    Checks if user is logged in. Used for public views where the functionality is different for authenticated users
    """
    try:
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        request.user_if_there_is_one = user
    except (KeyError, IndexError, InvalidToken, TokenError) as e:
        if isinstance(e, TokenError) and str(e) == 'Token is invalid or expired':
            raise HttpError(401, 'Token is invalid or expired')
        else:
            request.user_if_there_is_one = None
    return True


def thing_ownership_required(func):
    """
    Decorator for thing views that checks the user is logged in and is an owner of the related thing.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        jwt_auth(request)

        thing_id = kwargs.get('thing_id')
        try:
            thing = Thing.objects.get(id=thing_id)
        except Thing.DoesNotExist:
            raise HttpError(403, 'Site cannot be found')
        try:
            thing_association = request.authenticated_user.thing_associations.get(thing=thing, owns_thing=True)
        except ThingAssociation.DoesNotExist:
            raise HttpError(403, 'You do not have permission to access this site.')
        request.thing_association = thing_association
        request.thing = thing
        return func(request, *args, **kwargs)

    return wrapper


def datastream_ownership_required(func):
    """
    Decorator for datastream views that checks the user is logged in and is an owner of the related datastream's thing.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        jwt_auth(request)

        datastream_id = kwargs.get('datastream_id')
        try:
            datastream = Datastream.objects.get(id=datastream_id)
        except Datastream.DoesNotExist:
            return JsonResponse({'detail': 'Datastream not found.'}, status=404)
        request.datastream = datastream
        thing = datastream.thing

        try:
            thing_association = request.authenticated_user.thing_associations.get(thing=thing, owns_thing=True)
        except ThingAssociation.DoesNotExist:
            raise HttpError(403, 'You do not have permission to access this datastream.')
        request.thing_association = thing_association

        return func(request, *args, **kwargs)

    return wrapper


class GetTokenInput(Schema):
    email: str
    password: str


@api.post('/token')
def get_token(request, data: GetTokenInput):
    email = data.email
    password = data.password
    user = authenticate(username=email, password=password)
    if user:
        token = RefreshToken.for_user(user)
        return {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'user': user_to_dict(user)
        }
    else:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)


class CreateRefreshInput(Schema):
    refresh_token: str


@api.post("/token/refresh")
def refresh_token(request, data: CreateRefreshInput):
    try:
        token = data.refresh_token
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        new_token = RefreshToken.for_user(user)
        return JsonResponse({
            'access_token': str(new_token.access_token),
            'refresh_token': str(new_token),
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=401)
    except (InvalidToken, TokenError, KeyError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=401)


class PasswordResetRequestInput(Schema):
    email: str


@api.post("/password_reset")
def password_reset(request, data: PasswordResetRequestInput):
    try:
        user = CustomUser.objects.filter(email=data.email).first()
        if user:
            try:
                password_reset = PasswordReset(user=user)
                password_reset.save()
            except IntegrityError:
                PasswordReset.objects.get(user=user).delete()
                password_reset = PasswordReset(user=user)
                password_reset.save()

            token = default_token_generator.make_token(user)
            send_password_reset_email(user, password_reset.id, token)
            
            return JsonResponse({'message': 'Password reset email sent.'}, status=200)
        else:
            return JsonResponse({'detail': 'User does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def send_password_reset_email(user, uid, token):
    mail_subject = 'Password Reset'

    context = {
        'user': user,
        'uid': uid,
        'token': token,
        'domain': 'hydroserver.ciroh.org',  
        'proxy_base_url': PROXY_BASE_URL
    }

    html_message = render_to_string('reset_password_email.html', context)

    send_mail(
        mail_subject,
        '', # Don't support plain text emails
        'HydroServer <admin@hydroserver.ciroh.org>',
        [user.email],
        html_message=html_message,
    )


class ResetPasswordInput(Schema):
    uid: str
    token: str
    password: str

@api.post("/reset_password")
def reset_password(request, data: ResetPasswordInput):
    try:
        password_reset = PasswordReset.objects.get(pk=data.uid)
    except (PasswordReset.DoesNotExist):
        return JsonResponse({'error': 'Invalid UID'}, status=400)
        
    user = password_reset.user

    if not default_token_generator.check_token(user, data.token):
        return JsonResponse({'error': 'Invalid or expired token'}, status=400)

    user.set_password(data.password)
    user.save()
    password_reset.delete()

    return JsonResponse({'message': 'Password reset successful'}, status=200)


class CreateUserInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str = None
    organization: str = None


@api.post('/user')
def create_user(request, data: CreateUserInput):
    try:
        user = CustomUser.objects.create_user(
            username=data.email,
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            organization=data.organization,
            type=data.type,
            phone=data.phone,
            address=data.address
        )
    except IntegrityError:
        raise HttpError(400, 'EmailAlreadyExists')
    except Exception as e:
        raise HttpError(400, str(e))

    user = authenticate(username=data.email, password=data.password)
    user.save()

    token = RefreshToken.for_user(user)

    return {
        'access_token': str(token.access_token),
        'refresh_token': str(token),
    }


def user_to_dict(user):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "address": user.address,
        "organization": user.organization,
        "type": user.type
    }


# @api.get("/user", auth=jwt_auth)
# def get_user(request):
#     return JsonResponse(user_to_dict(request.authenticated_user))


class UpdateUserInput(Schema):
    first_name: str = None
    last_name: str = None
    middle_name: str = None
    phone: str = None
    address: str = None
    organization: str = None
    type: str = None


@api.patch('/user', auth=jwt_auth)
def update_user(request, data: UpdateUserInput):
    user = request.authenticated_user

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.middle_name is not None:
        user.middle_name = data.middle_name
    if data.phone is not None:
        user.phone = data.phone
    if data.address is not None:
        user.address = data.address
    if data.organization is not None:
        user.organization = data.organization
    if data.type is not None:
        user.type = data.type

    user.save()
    return JsonResponse(user_to_dict(user))


@api.delete('/user', auth=jwt_auth)
@transaction.atomic
def delete_user(request):
    try:
        Thing.objects.filter(associates__person=request.authenticated_user, associates__is_primary_owner=True).delete()
        request.authenticated_user.delete()
        logout(request)
        return {'detail': 'Your account has been removed!'}
    except CustomUser.DoesNotExist:
        raise HttpError(404, 'User not found')


def thing_to_dict(thing, user):
    thing_dict = {
        "id": thing.pk,
        "name": thing.name,
        "description": thing.description,
        "sampling_feature_type": thing.sampling_feature_type,
        "sampling_feature_code": thing.sampling_feature_code,
        "site_type": thing.site_type,
        "is_private": thing.is_private,
        "latitude": round(float(thing.location.latitude), 6),
        "longitude": round(float(thing.location.longitude), 6),
        "elevation": round(float(thing.location.elevation), 6),
        "state": thing.location.state,
        "county": thing.location.county,
        "is_primary_owner": False,
        "owns_thing": False,
        "follows_thing": False,
        "owners": [],
    }
    thing_associations = ThingAssociation.objects.filter(thing=thing)
    for thing_association in thing_associations:
        person = thing_association.person
        if thing_association.owns_thing:
            thing_dict['owners'].append({
                "firstname": person.first_name,
                "lastname": person.last_name,
                "organization": person.organization,
                "email": person.email,
                "is_primary_owner": thing_association.is_primary_owner
            })
    if user is not None:
        thing_association = thing_associations.filter(person=user).first()
        if thing_association:
            thing_dict.update({
                "is_primary_owner": thing_association.is_primary_owner,
                "owns_thing": thing_association.owns_thing,
                "follows_thing": thing_association.follows_thing,
            })
    return thing_dict


def photo_to_dict(photo):
    return {
        'id': photo.id, 
        'thingId': photo.thing.id, 
        'url': photo.url
        }

@api.post('/photos/{thing_id}', auth=jwt_auth)
@thing_ownership_required
def update_thing_photos(request, thing_id):
    try:
        s3 = boto3.client('s3', 
                            region_name='us-east-1', 
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        
        # First delete specified photos if there are any
        for photo_id in request.POST.getlist('photosToDelete', []):
            try:
                photo = Photo.objects.get(id=photo_id)
                photo.delete()
            except Photo.DoesNotExist:
                print(f"Photo {photo_id} does not exist")
                continue

        # Add new photos if there are any 
        photos_list = []
        for file in request.FILES.getlist('photos'):
            base, extension = os.path.splitext(file.name)
            file_name = f"{request.thing.id}/{uuid.uuid4()}{extension}"
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

            # Upload the photo to S3 bucket
            try:
                s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
            except ClientError as e:
                print(f"Error uploading {file_name} to S3: {e}")
                continue

            # Create a new photo in the database
            photo = Photo(thing=request.thing, url=file_url)
            photo.save()
            photos_list.append(photo_to_dict(photo))

        return JsonResponse([photo_to_dict(photo) for photo in request.thing.photos.all()], 
                            status=200, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api.get('/photos/{thing_id}')
def get_thing_photos(request, thing_id):
    try:
        thing = Thing.objects.get(id=thing_id)
        return JsonResponse([photo_to_dict(photo) for photo in thing.photos.all()], status=200, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


class ThingInput(Schema):
    name: str
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    latitude: float
    longitude: float
    elevation: float
    state: str = None
    county: str = None


@api.post('/things', auth=jwt_auth)
def create_thing(request, data: ThingInput):
    with transaction.atomic():
        new_thing = Thing.objects.create(name=data.name,
                                         description=data.description,
                                         sampling_feature_type=data.sampling_feature_type,
                                         sampling_feature_code=data.sampling_feature_code,
                                         site_type=data.site_type)

        Location.objects.create(name='Location for ' + new_thing.name,
                                description='location',
                                encoding_type="application/geo+json",
                                latitude=data.latitude, longitude=data.longitude, elevation=data.elevation,
                                state=data.state,
                                county=data.county,
                                thing=new_thing)

        ThingAssociation.objects.create(thing=new_thing, person=request.authenticated_user,
                                        owns_thing=True, is_primary_owner=True)

    return JsonResponse(thing_to_dict(new_thing, request.authenticated_user))


@api.get('/things', auth=jwt_check_user)
def get_things(request):
    if request.user_if_there_is_one:
        owned_things = ThingAssociation.objects.filter(
            person=request.user_if_there_is_one).values_list('thing', flat=True)
        things = Thing.objects.filter(Q(is_private=False) | Q(id__in=owned_things))
    else:
        things = Thing.objects.filter(is_private=False)
    return JsonResponse([thing_to_dict(thing, request.user_if_there_is_one) for thing in things], safe=False)


@api.get('/things/{thing_id}', auth=jwt_check_user)
def get_thing(request, thing_id: str):
    thing = Thing.objects.get(id=thing_id)
    thing_dict = thing_to_dict(thing, request.user_if_there_is_one)
    return JsonResponse(thing_dict)


class UpdateOwnershipInput(Schema):
    email: str
    make_owner: bool = False
    remove_owner: bool = False
    transfer_primary: bool = False


def transfer_properties_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's observed property from the old owner to the new owner.
    Checks if the old owner is assigned and correct, then searches for a matching property in
    the new owner's properties. If found, assigns this property to the datastream. If not found,
    creates a new property for the datastream. This way each owner keeps their own list of unique properties
    """
    if datastream.observed_property.person != old_owner or datastream.observed_property.person is None:
        return

    fields_to_compare = ['name', 'definition', 'description', 'variable_type', 'variable_code']
    same_properties = ObservedProperty.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.observed_property, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.observed_property = same_properties[0]
    else:
        new_property = copy.copy(datastream.observed_property)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.observed_property = new_property

    datastream.save()


def transfer_processing_level_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's processing level from the old owner to the new owner.
    """
    if datastream.processing_level.person != old_owner or datastream.processing_level.person is None:
        return

    fields_to_compare = ['processing_level_code', 'definition', 'explanation']
    same_properties = ProcessingLevel.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.processing_level, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.processing_level = same_properties[0]
    else:
        new_property = copy.copy(datastream.processing_level)
        new_property.id = None  # Set to None so Django can auto-generate a new unique integer id
        new_property.person = new_owner
        new_property.save()
        datastream.processing_level = new_property

    datastream.save()


def transfer_unit_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's unit from the old owner to the new owner.
    """
    if datastream.unit.person != old_owner or datastream.unit.person is None:
        return

    fields_to_compare = ['name', 'symbol', 'definition', 'unit_type']

    same_properties = Unit.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.unit, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.unit = same_properties[0]
    else:
        new_property = copy.copy(datastream.unit)
        new_property.id = None  # Set to None so Django can auto-generate a new unique integer id
        new_property.person = new_owner
        new_property.save()
        datastream.unit = new_property

    datastream.save()


def transfer_sensor_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's sensor from the old owner to the new owner.
    """
    if datastream.sensor.person != old_owner or datastream.sensor.person is None:
        return

    fields_to_compare = ['name', 'description', 'encoding_type', 'manufacturer', 'model', 'model_url',
                         'method_type', 'method_link', 'method_code']

    same_properties = Sensor.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.sensor, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.sensor = same_properties[0]
    else:
        new_property = copy.copy(datastream.sensor)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.sensor = new_property

    datastream.save()


@api.patch('/things/{thing_id}/ownership', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def update_thing_ownership(request, thing_id: str, data: UpdateOwnershipInput):
    flags = [data.make_owner, data.remove_owner, data.transfer_primary]
    if sum(flag is True for flag in flags) != 1:
        return JsonResponse(
            {"error": "Only one action (make_owner, remove_owner, transfer_primary) should be true."}, status=400)

    try:
        user = CustomUser.objects.get(email=data.email)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "Specified user not found."}, status=404)

    current_user_association = ThingAssociation.objects.get(thing=request.thing, person=request.authenticated_user)

    if request.authenticated_user == user and current_user_association.is_primary_owner:
        return JsonResponse({"error": "Primary owner cannot edit their own ownership."}, status=403)
    if not current_user_association.is_primary_owner and user != request.authenticated_user:
        return JsonResponse({"error": "Only the primary owner can modify other users' ownership."}, status=403)

    thing_association, created = ThingAssociation.objects.get_or_create(thing=request.thing, person=user)

    if data.transfer_primary:
        if not current_user_association.is_primary_owner:
            return JsonResponse({"error": "Only primary owner can transfer primary ownership."}, status=403)
        datastreams = request.thing.datastreams.all()
        for datastream in datastreams:
            transfer_properties_ownership(datastream, user, request.authenticated_user)
            transfer_processing_level_ownership(datastream, user, request.authenticated_user)
            transfer_unit_ownership(datastream, user, request.authenticated_user)
            transfer_sensor_ownership(datastream, user, request.authenticated_user)
        current_user_association.is_primary_owner = False
        current_user_association.save()
        thing_association.is_primary_owner = True
        thing_association.owns_thing = True
    elif data.remove_owner:
        if thing_association.is_primary_owner:
            return JsonResponse({"error": "Cannot remove primary owner."}, status=400)
        thing_association.delete()
        return JsonResponse(thing_to_dict(request.thing, request.authenticated_user), status=200)
    elif data.make_owner:
        thing_association.owns_thing = True

    thing_association.follows_thing = False
    thing_association.save()
    return JsonResponse(thing_to_dict(request.thing, request.authenticated_user), status=200)


class UpdateThingPrivacy(Schema):
    is_private: bool


@api.patch('/things/{thing_id}/privacy', auth=jwt_auth)
@thing_ownership_required
def update_thing_privacy(request, thing_id: str, data: UpdateThingPrivacy):
    thing = request.thing
    thing.is_private = data.is_private
    thing_associations = ThingAssociation.objects.filter(thing=thing)

    if data.is_private:
        for thing_association in thing_associations:
            if thing_association.follows_thing:
                thing_association.delete()

    thing.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user))


@api.patch('/things/{thing_id}/followership', auth=jwt_auth)
def update_thing_followership(request, thing_id: str):
    thing = Thing.objects.get(id=thing_id)

    if request.authenticated_user.thing_associations.filter(thing=thing, owns_thing=True).exists():
        return JsonResponse({"error": "Owners cannot update follow status"}, status=400)

    thing_association, created = ThingAssociation.objects.get_or_create(thing=thing, person=request.authenticated_user)

    if thing_association.follows_thing:
        thing_association.delete()
    else:
        thing_association.follows_thing = True
        thing_association.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user))


class UpdateThingInput(Schema):
    name: str = None
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    latitude: float = None
    longitude: float = None
    elevation: float = None
    city: str = None
    state: str = None
    county: str = None


@api.patch('/things/{thing_id}')
@thing_ownership_required
def update_thing(request, thing_id: str, data: UpdateThingInput):
    thing = request.thing
    location = Location.objects.get(thing=thing)

    if data.name is not None:
        thing.name = data.name
        location.name = 'Location for ' + data.name
    if data.description is not None:
        thing.description = data.description
    if data.sampling_feature_type is not None:
        thing.sampling_feature_type = data.sampling_feature_type
    if data.sampling_feature_code is not None:
        thing.sampling_feature_code = data.sampling_feature_code
    if data.site_type is not None:
        thing.site_type = data.site_type

    if data.latitude is not None:
        location.latitude = data.latitude
    if data.longitude is not None:
        location.longitude = data.longitude
    if data.elevation is not None:
        location.elevation = data.elevation
    if data.city is not None:
        location.city = data.city
    if data.state is not None:
        location.state = data.state
    if data.county is not None:
        location.county = data.county

    thing.save()
    location.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user), status=200)


@api.delete('/things/{thing_id}')
@thing_ownership_required
def delete_thing(request, thing_id: str):
    try:
        request.thing.delete()
    except Exception as e:
        return JsonResponse(status=500, detail=str(e))

    return JsonResponse({'detail': 'Site deleted successfully.'}, status=200)

def sensor_to_dict(sensor):
    return {
        "id": sensor.pk,
        "name": sensor.name,
        "description": sensor.description,
        "manufacturer": sensor.manufacturer,
        "model": sensor.model,
        "method_type": sensor.method_type,
        "method_code": sensor.method_code,
        "method_link": sensor.method_link,
        "encoding_type": sensor.encoding_type,
        "model_url": sensor.model_url,
    }


class SensorInput(Schema):
    name: str = None
    description: str = None
    encoding_type: str = None
    manufacturer: str = None
    model: str = None
    model_url: str = None
    method_type: str = None
    method_link: str = None
    method_code: str = None


@api.post('/sensors', auth=jwt_auth)
def create_sensor(request, data: SensorInput):
    sensor = Sensor.objects.create(
        person=request.authenticated_user,
        name=data.name,
        description=data.description,
        manufacturer=data.manufacturer,
        model=data.model,
        method_type=data.method_type,
        method_code=data.method_code,
        method_link=data.method_link,
        encoding_type=data.encoding_type,
        model_url=data.model_url,
    )

    return JsonResponse(sensor_to_dict(sensor))


@api.get('/sensors', auth=jwt_auth)
def get_sensors(request):
    sensors = Sensor.objects.filter(Q(person=request.authenticated_user))
    return JsonResponse([sensor_to_dict(sensor) for sensor in sensors], safe=False)


@api.patch('/sensors/{sensor_id}', auth=jwt_auth)
def update_sensor(request, sensor_id: str, data: SensorInput):
    sensor = Sensor.objects.get(id=sensor_id)
    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to update this sensor.'}, status=403)

    if data.name is not None:
        sensor.name = data.name
    if data.description is not None:
        sensor.description = data.description
    if data.manufacturer is not None:
        sensor.manufacturer = data.manufacturer
    if data.model is not None:
        sensor.model = data.model
    if data.method_type is not None:
        sensor.method_type = data.method_type
    if data.method_code is not None:
        sensor.method_code = data.method_code
    if data.method_link is not None:
        sensor.method_link = data.method_link
    if data.encoding_type is not None:
        sensor.encoding_type = data.encoding_type
    if data.model_url is not None:
        sensor.model_url = data.model_url

    sensor.save()

    return JsonResponse(sensor_to_dict(sensor))


@api.delete('/sensors/{sensor_id}', auth=jwt_auth)
def delete_sensor(request, sensor_id: str):
    try:
        sensor = Sensor.objects.get(id=sensor_id)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to delete this sensor.'}, status=403)

    sensor.delete()

    return {'detail': 'Sensor deleted successfully.'}


def observed_property_to_dict(observed_property):
    return {
        "id": observed_property.pk,
        "name": observed_property.name,
        "definition": observed_property.definition,
        "description": observed_property.description,
        "variable_type": observed_property.variable_type,
        "variable_code": observed_property.variable_code,
    }


@api.get('/observed-properties', auth=jwt_auth)
def get_observed_properties(request):
    observed_properties = ObservedProperty.objects.filter(Q(person=request.authenticated_user))
    return JsonResponse([observed_property_to_dict(op) for op in observed_properties], safe=False)


class ObservedPropertyInput(Schema):
    name: str
    definition: str
    description: str
    variable_type: str = None
    variable_code: str = None


@api.post('/observed-properties', auth=jwt_auth)
def create_observed_property(request, data: ObservedPropertyInput):
    observed_property = ObservedProperty.objects.create(
        name=data.name,
        person=request.authenticated_user,
        definition=data.definition,
        description=data.description,
        variable_type=data.variable_type,
        variable_code=data.variable_code
    )
    return JsonResponse(observed_property_to_dict(observed_property))


@api.patch('/observed-properties/{observed_property_id}', auth=jwt_auth)
def update_observed_property(request, observed_property_id: str, data: ObservedPropertyInput):
    observed_property = ObservedProperty.objects.get(id=observed_property_id)
    if request.authenticated_user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to update this observed property.'}, status=403)

    if data.name is not None:
        observed_property.name = data.name
    if data.definition is not None:
        observed_property.definition = data.definition
    if data.description is not None:
        observed_property.description = data.description
    if data.variable_type is not None:
        observed_property.variable_type = data.variable_type
    if data.variable_code is not None:
        observed_property.variable_code = data.variable_code

    observed_property.save()

    return JsonResponse(observed_property_to_dict(observed_property))


@api.delete('/observed-properties/{observed_property_id}', auth=jwt_auth)
def delete_observed_property(request, observed_property_id: str):
    try:
        observed_property = ObservedProperty.objects.get(id=observed_property_id)
    except ObservedProperty.DoesNotExist:
        return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    if request.authenticated_user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to delete this observed property.'}, status=403)

    observed_property.delete()

    return {'detail': 'Observed Property deleted successfully.'}


class CreateDatastreamInput(Schema):
    thing_id: str
    method_id: str
    observed_property_id: str
    processing_level_id: str = None
    unit_id: str = None

    observation_type: str = None
    result_type: str = None
    status: str = None
    sampled_medium: str = None
    value_count: str = None
    no_data_value: str = None
    intended_time_spacing: str = None
    intended_time_spacing_units: str = None

    aggregation_statistic: str = None
    time_aggregation_interval: str = None
    time_aggregation_interval_units: str = None

    phenomenon_start_time: str = None
    phenomenon_end_time: str = None
    result_begin_time: str = None
    result_end_time: str = None


def datastream_to_dict(datastream, association=None, add_recent_observations=True):
    observation_list = []
    most_recent_observation = None
    is_stale = True
    if add_recent_observations:
        if datastream.result_end_time:
            if datastream.result_end_time > timezone.now() - timedelta(hours=72):
                is_stale = False
            since_time = datastream.result_end_time - timedelta(hours=72)
            observations = Observation.objects.filter(datastream=datastream, result_time__gte=since_time).order_by('-result_time')
            for observation in observations:
                observation_list.append({
                    "id": observation.id,
                    "result": observation.result,
                    "result_time": observation.result_time,
                })
            if observation_list:
                most_recent_observation = observation_list[0]

    return {
        "id": datastream.pk,
        "thing_id": datastream.thing.id,
        "observation_type": datastream.observation_type,
        "result_type": datastream.result_type,
        "status": datastream.status,
        "sampled_medium": datastream.sampled_medium,
        "no_data_value": datastream.no_data_value,
        "aggregation_statistic": datastream.aggregation_statistic,
        "observations": observation_list if observation_list else None,
        "most_recent_observation": most_recent_observation,

        "unit_id": datastream.unit.pk if datastream.unit else None,
        "observed_property_id": datastream.observed_property.pk if datastream.observed_property else None,
        "method_id": datastream.sensor.pk if datastream.sensor else None,
        "processing_level_id": datastream.processing_level.pk if datastream.processing_level else None,

        "unit_name": datastream.unit.name if datastream.unit else None,
        "observed_property_name": datastream.observed_property.name if datastream.observed_property else None,
        "method_name": datastream.sensor.name if datastream.sensor else None,
        "processing_level_name": datastream.processing_level.processing_level_code if datastream.processing_level else None,
        "is_visible": datastream.is_visible,
        "is_primary_owner": association.is_primary_owner if association else False,
        "is_stale": is_stale,
    }


@api.post('/datastreams/{thing_id}', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def create_datastream(request, thing_id, data: CreateDatastreamInput):
    try:
        sensor = Sensor.objects.get(id=data.method_id)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    try:
        observed_property = ObservedProperty.objects.get(id=data.observed_property_id)
    except ObservedProperty.DoesNotExist:
        return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    try:
        unit = Unit.objects.get(id=data.unit_id) if data.unit_id else None
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if data.processing_level_id:
        processing_level = ProcessingLevel.objects.get(id=data.processing_level_id)
    else:
        processing_level = None

    datastream = Datastream.objects.create(
        description="Site Datastream",
        observed_property=observed_property,
        unit=unit,
        processing_level=processing_level,
        sampled_medium=data.sampled_medium,
        status=data.status,
        no_data_value=float(data.no_data_value) if data.no_data_value else None,
        aggregation_statistic=data.aggregation_statistic,
        result_type=data.result_type if data.result_type else 'Time Series Coverage',
        observation_type=data.observation_type if data.observation_type else 'OM_Measurement',
        thing=request.thing,
        sensor=sensor,
    )

    return JsonResponse(datastream_to_dict(datastream, request.thing_association))


@api.get('/datastreams', auth=jwt_auth)
def get_datastreams(request):
    user_associations = ThingAssociation.objects.filter(
        person=request.authenticated_user,
        owns_thing=True
    ).prefetch_related('thing__datastreams')

    user_datastreams = [
        datastream_to_dict(datastream, association)
        for association in user_associations
        for datastream in association.thing.datastreams.all()
    ]

    return JsonResponse(user_datastreams, safe=False)


def get_public_datastreams(thing_id: str):
    try:
        thing = Thing.objects.get(pk=thing_id)
    except Thing.DoesNotExist:
        return JsonResponse({'detail': 'Site not found.'}, status=404)
    return JsonResponse([
        datastream_to_dict(datastream) 
        for datastream in thing.datastreams.all() if datastream.is_visible], safe=False)


@api.get('/datastreams/{thing_id}', auth=jwt_check_user)
def get_datastreams_for_thing(request, thing_id: str):
    if request.user_if_there_is_one:
        try:
            user_association = ThingAssociation.objects.get(
                person=request.user_if_there_is_one,
                thing_id=thing_id,
                owns_thing=True,
            )
        except ThingAssociation.DoesNotExist:
            return get_public_datastreams(thing_id=thing_id)
        return JsonResponse([
            datastream_to_dict(datastream, user_association)
            for datastream in user_association.thing.datastreams.all()
        ], safe=False)
    else:
        return get_public_datastreams(thing_id=thing_id)


class UpdateDatastreamInput(Schema):
    unit_id: str = None
    method_id: str = None
    observed_property_id: str = None
    processing_level_id: str = None

    observation_type: str = None
    result_type: str = None
    status: str = None
    sampled_medium: str = None
    value_count: str = None
    no_data_value: str = None
    intended_time_spacing: str = None
    intended_time_spacing_units: str = None

    aggregation_statistic: str = None
    time_aggregation_interval: str = None
    time_aggregation_interval_units: str = None

    phenomenon_start_time: str = None
    phenomenon_end_time: str = None
    result_begin_time: str = None
    result_end_time: str = None
    is_visible: bool = None


@api.patch('/datastreams/patch/{datastream_id}', auth=jwt_auth)
@datastream_ownership_required
@transaction.atomic
def update_datastream(request, datastream_id: str, data: UpdateDatastreamInput):
    datastream = request.datastream
    
    if data.method_id is not None:
        try:
            datastream.sensor = Sensor.objects.get(id=data.method_id)
        except Sensor.DoesNotExist:
            return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    if data.observed_property_id is not None:
        try:
            datastream.observed_property = ObservedProperty.objects.get(id=data.observed_property_id)
        except ObservedProperty.DoesNotExist:
            return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    if data.unit_id is not None:
        try:
            datastream.unit = Unit.objects.get(id=data.unit_id)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if data.processing_level_id is not None:
        try:
            datastream.processing_level = ProcessingLevel.objects.get(id=data.processing_level_id)
        except ProcessingLevel.DoesNotExist:
            return JsonResponse({'detail': 'Processing Level not found.'}, status=404)

    if data.observation_type is not None:
        datastream.observation_type = data.observation_type
    if data.result_type is not None:
        datastream.result_type = data.result_type
    if data.status is not None:
        datastream.status = data.status
    if data.sampled_medium is not None:
        datastream.sampled_medium = data.sampled_medium
    if data.no_data_value is not None:
        datastream.no_data_value = data.no_data_value
    if data.aggregation_statistic is not None:
        datastream.aggregation_statistic = data.aggregation_statistic
    if data.time_aggregation_interval is not None:
        datastream.time_aggregation_interval = data.time_aggregation_interval
    if data.time_aggregation_interval_units is not None:
        try:
            datastream.time_aggregation_interval_units = Unit.objects.get(id=data.time_aggregation_interval_units)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'time_aggregation_interval_units not found.'}, status=404)
    if data.phenomenon_start_time is not None:
        datastream.phenomenon_start_time = data.phenomenon_start_time
    if data.phenomenon_end_time is not None:
        datastream.phenomenon_end_time = data.phenomenon_end_time
    if data.result_begin_time is not None:
        datastream.result_begin_time = data.result_begin_time
    if data.result_end_time is not None:
        datastream.result_end_time = data.result_end_time
    if data.value_count is not None:
        datastream.value_count = data.value_count
    if data.intended_time_spacing is not None:
        datastream.intended_time_spacing = data.intended_time_spacing
    if data.intended_time_spacing_units is not None:
        try:
            datastream.intended_time_spacing_units = Unit.objects.get(id=data.intended_time_spacing_units)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'intended_time_spacing_units not found.'}, status=404)
    if data.is_visible is not None:
        datastream.is_visible = data.is_visible

    datastream.save()

    return JsonResponse(datastream_to_dict(datastream, request.thing_association))


@api.delete('/datastreams/{datastream_id}/temp')
@datastream_ownership_required
@transaction.atomic()
def delete_datastream(request, datastream_id: str):
    try:
        request.datastream.delete()
    except Exception as e:
        return JsonResponse(status=500, detail=str(e))

    return JsonResponse({'detail': 'Datastream deleted successfully.'}, status=200)


def unit_to_dict(unit):
    return {
        "id": unit.pk,
        "name": unit.name,
        "symbol": unit.symbol,
        "definition": unit.definition,
        "unit_type": unit.unit_type,
        "person_id": unit.person.pk if unit.person else None
    }


@api.get('/units', auth=jwt_auth)
def get_units(request):
    units = Unit.objects.filter(Q(person=request.authenticated_user) | Q(person__isnull=True))
    return JsonResponse([unit_to_dict(unit) for unit in units], safe=False)


@api.get('/things/{thing_id}/metadata', auth=jwt_auth)
@thing_ownership_required
def get_primary_owner_metadata(request, thing_id):
    thing_associations = ThingAssociation.objects.filter(thing=request.thing, is_primary_owner=True)
    primary_owner = thing_associations.first().person if thing_associations.exists() else None

    if not primary_owner:
        return JsonResponse({'error': 'Primary owner cannot be found for thing'}, status=401)
    units = Unit.objects.filter(Q(person=primary_owner) | Q(person__isnull=True))
    sensors = Sensor.objects.filter(Q(person=primary_owner))
    processing_levels = ProcessingLevel.objects.filter(Q(person=primary_owner) | Q(person__isnull=True))
    observed_properties = ObservedProperty.objects.filter(Q(person=primary_owner))

    unit_data = [unit_to_dict(unit) for unit in units]
    sensor_data = [sensor_to_dict(sensor) for sensor in sensors]
    processing_level_data = [processing_level_to_dict(pl) for pl in processing_levels]
    observed_property_data = [observed_property_to_dict(op) for op in observed_properties]

    return JsonResponse({
        'units': unit_data,
        'sensors': sensor_data,
        'processing_levels': processing_level_data,
        'observed_properties': observed_property_data
    })


class CreateUnitInput(Schema):
    name: str
    symbol: str
    definition: str
    unit_type: str


@api.post('/units', auth=jwt_auth)
def create_unit(request, data: CreateUnitInput):
    unit = Unit.objects.create(
        name=data.name,
        person=request.authenticated_user,
        symbol=data.symbol,
        definition=data.definition,
        unit_type=data.unit_type
    )
    return JsonResponse(unit_to_dict(unit))


class UpdateUnitInput(Schema):
    name: str
    symbol: str
    definition: str
    unit_type: str


@api.patch('/units/{unit_id}', auth=jwt_auth)
def update_unit(request, unit_id: str, data: UpdateUnitInput):
    unit = Unit.objects.get(id=unit_id)
    if request.authenticated_user != unit.person:
        return JsonResponse({'detail': 'You are not authorized to update this unit.'}, status=403)

    if data.name is not None:
        unit.name = data.name
    if data.symbol is not None:
        unit.symbol = data.symbol
    if data.definition is not None:
        unit.definition = data.definition
    if data.unit_type is not None:
        unit.unit_type = data.unit_type

    unit.save()
    return JsonResponse(unit_to_dict(unit))


@api.delete('/units/{unit_id}', auth=jwt_auth)
def delete_unit(request, unit_id: str):
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if request.authenticated_user != unit.person:
        return JsonResponse({'detail': 'You are not authorized to delete this unit.'}, status=403)

    unit.delete()
    return {'detail': 'Unit deleted successfully.'}


class ProcessingLevelInput(Schema):
    processing_level_code: str
    definition: str
    explanation: str


def processing_level_to_dict(processing_level):
    return {
        "id": processing_level.pk,
        "processing_level_code": processing_level.processing_level_code,
        "definition": processing_level.definition,
        "explanation": processing_level.explanation,
        "person_id": processing_level.person.pk if processing_level.person else None
    }


@api.get('/processing-levels', auth=jwt_auth)
def get_processing_levels(request):
    processing_levels = ProcessingLevel.objects.filter(Q(person=request.authenticated_user) | Q(person__isnull=True))
    return JsonResponse([processing_level_to_dict(pl) for pl in processing_levels], safe=False)


@api.post('/processing-levels', auth=jwt_auth)
def create_processing_level(request, data: ProcessingLevelInput):
    processing_level = ProcessingLevel.objects.create(
        person=request.authenticated_user,
        processing_level_code=data.processing_level_code,
        definition=data.definition,
        explanation=data.explanation,
    )

    return JsonResponse(processing_level_to_dict(processing_level))


@api.patch('/processing-levels/{processing_level_id}', auth=jwt_auth)
def update_processing_level(request, processing_level_id: str, data: ProcessingLevelInput):
    processing_level = ProcessingLevel.objects.get(id=processing_level_id)
    if request.authenticated_user != processing_level.person:
        return JsonResponse({'detail': 'You are not authorized to update this processing level.'}, status=403)

    if data.processing_level_code is not None:
        processing_level.processing_level_code = data.processing_level_code
    if data.definition is not None:
        processing_level.definition = data.definition
    if data.explanation is not None:
        processing_level.explanation = data.explanation

    processing_level.save()

    return JsonResponse(processing_level_to_dict(processing_level))


@api.delete('/processing-levels/{processing_level_id}', auth=jwt_auth)
def delete_processing_level(request, processing_level_id: str):
    try:
        pl = ProcessingLevel.objects.get(id=processing_level_id)
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'processing level not found.'}, status=404)

    if request.authenticated_user != pl.person:
        return JsonResponse({'detail': 'You are not authorized to delete this unit.'}, status=403)

    pl.delete()
    return {'detail': 'Processing level deleted successfully.'}


class DataLoaderGetResponse(Schema):
    id: UUID
    name: str


class DataLoaderPostBody(Schema):
    name: str


@allow_partial
class DataLoaderPatchBody(Schema):
    name: str


@api.get(
    '/data-loaders',
    url_name='get_data_loaders',
    response={
        200: List[DataLoaderGetResponse]
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_loaders(request: HttpRequest):

    data_loaders = DataLoader.objects.filter(dataloaderowner__person=request.authenticated_user)

    return [
        {
            'id': data_loader.id,
            'name': data_loader.name
        } for data_loader in data_loaders
    ]


@api.get(
    '/data-loaders/{data_loader_id}',
    url_name='get_data_loader',
    response={
        200: DataLoaderGetResponse,
        404: None
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_loader(request: HttpRequest, data_loader_id: str):

    data_loader = DataLoader.objects.get(dataloaderowner__person=request.authenticated_user, pk=data_loader_id)

    return {
        'id': data_loader.id,
        'name': data_loader.name
    }


@api.post(
    '/data-loaders',
    url_name='create_data_loader',
    response={
        201: None
    },
    auth=[BasicAuth(), jwt_auth]
)
@transaction.atomic
def post_data_loader(request: HttpRequest, data_loader: DataLoaderPostBody):
    """"""

    new_data_loader = DataLoader.objects.create(
        name=data_loader.name,
    )

    DataLoaderOwner.objects.create(
        data_loader=new_data_loader,
        person=request.authenticated_user
    )

    return None


@api.patch(
    '/data-loaders/{data_loader_id}',
    url_name='update_data_loader',
    response={
        204: None
    },
    auth=[BasicAuth(), jwt_auth],
)
@transaction.atomic
def patch_data_loader(request: HttpRequest, data_loader_id: str, data_loader: DataLoaderPatchBody):
    """"""

    data_loader = data_loader.dict(exclude_unset=True)
    data_loader_db = DataLoader.objects.filter(
        pk=data_loader_id,
        dataloaderowner__person=request.authenticated_user,
    )[0]

    if 'name' in data_loader:
        data_loader_db.name = data_loader['name']

    data_loader_db.save()

    return None


@api.delete(
    '/data-loaders/{data_loader_id}',
    auth=[BasicAuth(), jwt_auth],
    response={
        200: None,
        403: None,
        404: None
    },
)
def delete_data_loader(request: HttpRequest, data_loader_id: str):
    try:
        data_loader = DataLoader.objects.get(id=data_loader_id)
    except DataLoader.DoesNotExist:
        return 404, f'Data Loader with ID: {data_loader_id} does not exist.'

    if request.authenticated_user not in [
        data_loader_owner.person for data_loader_owner
        in data_loader.dataloaderowner_set.filter(is_primary_owner=True)
    ]:
        return 403, 'You do not have permission to delete this data loader.'

    data_loader.delete()

    return 200


class DataSourceDatastream(Schema):
    id: UUID
    name: str
    description: str
    result_start_time: Optional[datetime]
    result_end_time: Optional[datetime]
    column: Union[int, str]


class DataSourceGetResponse(HydroLoaderConf):
    id: UUID
    name: str
    datastreams: List[DataSourceDatastream]
    data_loader: Optional[DataLoaderGetResponse]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]
    database_thru_upper: Optional[datetime]
    database_thru_lower: Optional[datetime]


class DataSourcePostBody(HydroLoaderConf):
    name: str
    data_loader: Optional[UUID]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]


@allow_partial
class DataSourcePatchBody(HydroLoaderConf):
    name: str
    data_loader: Optional[UUID]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]


def transform_data_source(data_source):
    return DataSourceGetResponse(
        id=data_source.id,
        name=data_source.name,
        data_source_thru=data_source.data_source_thru,
        last_sync_successful=data_source.last_sync_successful,
        last_sync_message=data_source.last_sync_message,
        last_synced=data_source.last_synced,
        next_sync=data_source.next_sync,
        data_loader=DataLoaderGetResponse(
            id=data_source.data_loader.id,
            name=data_source.data_loader.name
        ) if data_source.data_loader else None,
        database_thru_upper=max([
            datastream.result_end_time for datastream in data_source.datastream_set.all()
            if datastream.result_end_time is not None
        ], default=None),
        database_thru_lower=min([
            datastream.result_end_time for datastream in data_source.datastream_set.all()
            if datastream.result_end_time is not None
        ], default=None),
        file_access=HydroLoaderConfFileAccess(
            path=data_source.path,
            url=data_source.url,
            header_row=data_source.header_row,
            data_start_row=data_source.data_start_row,
            delimiter=data_source.delimiter,
            quote_char=data_source.quote_char
        ),
        schedule=HydroLoaderConfSchedule(
            crontab=data_source.crontab,
            interval=data_source.interval,
            interval_units=data_source.interval_units,
            start_time=data_source.start_time,
            end_time=data_source.end_time,
            paused=data_source.paused
        ),
        file_timestamp=HydroLoaderConfFileTimestamp(
            column=data_source.timestamp_column,
            format=data_source.timestamp_format,
            offset=data_source.timestamp_offset
        ),
        datastreams=[
            DataSourceDatastream(
                id=datastream.id,
                name=datastream.name,
                description=datastream.description,
                result_start_time=datastream.result_begin_time,
                result_end_time=datastream.result_end_time,
                column=datastream.data_source_column
            ) for datastream in data_source.datastream_set.all()
        ]
    )


@api.get(
    '/data-sources',
    url_name='get_data_sources',
    response={
        200: List[DataSourceGetResponse]
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_sources(request: HttpRequest):

    data_sources = DataSource.objects.filter(datasourceowner__person=request.authenticated_user)

    return [
        transform_data_source(data_source) for data_source in data_sources
    ]


@api.get(
    '/data-sources/{data_source_id}',
    url_name='get_data_source',
    response={
        200: DataSourceGetResponse,
        404: None
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_source(request: HttpRequest, data_source_id: str):

    data_source = DataSource.objects.get(datasourceowner__person=request.authenticated_user, pk=data_source_id)

    return transform_data_source(data_source)


@api.post(
    '/data-sources',
    url_name='create_data_source',
    response={
        201: None
    },
    auth=[BasicAuth(), jwt_auth]
)
@transaction.atomic
def post_data_source(request: HttpRequest, data_source: DataSourcePostBody):
    """"""

    new_data_source = DataSource.objects.create(
        name=data_source.name,
        data_loader_id=data_source.data_loader,
        path=data_source.file_access.path,
        url=data_source.file_access.url,
        header_row=data_source.file_access.header_row,
        data_start_row=data_source.file_access.data_start_row,
        delimiter=data_source.file_access.delimiter,
        quote_char=data_source.file_access.quote_char,
        interval=data_source.schedule.interval,
        interval_units=data_source.schedule.interval_units,
        crontab=data_source.schedule.crontab,
        start_time=data_source.schedule.start_time,
        end_time=data_source.schedule.end_time,
        paused=data_source.schedule.paused if data_source.schedule.paused is not None else False,
        timestamp_column=data_source.file_timestamp.column,
        timestamp_format=data_source.file_timestamp.format,
        timestamp_offset=data_source.file_timestamp.offset,
        data_source_thru=data_source.data_source_thru,
        last_sync_successful=data_source.last_sync_successful,
        last_sync_message=data_source.last_sync_message,
        last_synced=data_source.last_synced,
        next_sync=data_source.next_sync
    )

    DataSourceOwner.objects.create(
        data_source=new_data_source,
        person=request.authenticated_user,
        is_primary_owner=True
    )

    for datastream in data_source.datastreams:

        datastream_db = Datastream.objects.get(pk=datastream.datastream_id)
        request.authenticated_user.thing_associations.get(
            thing=datastream_db.thing,
            owns_thing=True
        )
        datastream_db.data_source = new_data_source
        datastream_db.data_source_column = datastream.column
        datastream_db.save()

    return None


@api.patch(
    '/data-sources/{data_source_id}',
    url_name='update_data_source',
    response={
        204: None
    },
    auth=[BasicAuth(), jwt_auth],
)
@transaction.atomic
def patch_data_source(request: HttpRequest, data_source_id: str, data_source: DataSourcePatchBody):
    """"""

    data_source = data_source.dict(exclude_unset=True)
    data_source_db = DataSource.objects.filter(
        pk=data_source_id,
        datasourceowner__person=request.authenticated_user,
    )[0]

    if 'name' in data_source:
        data_source_db.name = data_source['name']
    if 'data_loader' in data_source:
        data_source_db.data_loader_id = data_source['data_loader']
    if 'data_source_thru' in data_source:
        data_source_db.data_source_thru = data_source['data_source_thru']
    if 'last_sync_successful' in data_source:
        data_source_db.last_sync_successful = data_source['last_sync_successful']
    if 'last_sync_message' in data_source:
        data_source_db.last_sync_message = data_source['last_sync_message']
    if 'last_synced' in data_source:
        data_source_db.last_synced = data_source['last_synced']
    if 'next_sync' in data_source:
        data_source_db.next_sync = data_source['next_sync']

    if 'path' in data_source.get('file_access', {}):
        data_source_db.path = data_source['file_access']['path']
    if 'url' in data_source.get('file_access', {}):
        data_source_db.url = data_source['file_access']['url']
    if 'header_row' in data_source.get('file_access', {}):
        data_source_db.header_row = data_source['file_access']['header_row']
    if 'data_start_row' in data_source.get('file_access', {}):
        data_source_db.data_start_row = data_source['file_access']['data_start_row']
    if 'delimiter' in data_source.get('file_access', {}):
        data_source_db.delimiter = data_source['file_access']['delimiter']
    if 'quote_char' in data_source.get('file_access', {}):
        data_source_db.quote_char = data_source['file_access']['quote_char']

    if 'interval' in data_source.get('schedule', {}):
        data_source_db.interval = data_source['schedule']['interval']
    if 'interval_units' in data_source.get('schedule', {}):
        data_source_db.interval_units = data_source['schedule']['interval_units']
    if 'crontab' in data_source.get('schedule', {}):
        data_source_db.crontab = data_source['schedule']['crontab']
    if 'start_time' in data_source.get('schedule', {}):
        data_source_db.start_time = data_source['schedule']['start_time']
    if 'end_time' in data_source.get('schedule', {}):
        data_source_db.end_time = data_source['schedule']['end_time']
    if 'paused' in data_source.get('schedule', {}):
        data_source_db.paused = data_source['schedule']['paused'] if data_source['schedule']['paused'] \
                                                                     is not None else False

    if 'column' in data_source.get('file_timestamp', {}):
        data_source_db.timestamp_column = data_source['file_timestamp']['column']
    if 'format' in data_source.get('file_timestamp', {}):
        data_source_db.timestamp_format = data_source['file_timestamp']['format']
    if 'offset' in data_source.get('file_timestamp', {}):
        data_source_db.timestamp_offset = data_source['file_timestamp']['offset']

    data_source_db.save()

    for datastream in data_source.get('datastreams', []):
        datastream_db = Datastream.objects.get(pk=datastream['id'])
        request.authenticated_user.thing_associations.get(
            thing=datastream_db.thing,
            owns_thing=True
        )
        datastream_db.data_source = data_source_db
        datastream_db.data_source_column = datastream['column']
        datastream_db.save()


@api.delete(
    '/data-sources/{data_source_id}',
    auth=[BasicAuth(), jwt_auth],
    response={
        200: None,
        403: None,
        404: None
    },
)
def delete_data_source(request: HttpRequest, data_source_id: str):
    try:
        data_source = DataSource.objects.get(id=data_source_id)
    except DataSource.DoesNotExist:
        return 404, f'Data Source with ID: {data_source_id} does not exist.'

    if request.authenticated_user not in [
        data_source_owner.person for data_source_owner
        in data_source.datasourceowner_set.filter(is_primary_owner=True)
    ]:
        return 403, 'You do not have permission to delete this data source.'

    data_source.delete()

    return 200
