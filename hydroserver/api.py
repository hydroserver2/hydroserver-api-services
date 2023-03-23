import datetime
import json
import uuid

from _decimal import Decimal
from django.contrib.auth import authenticate
from django.http import JsonResponse
from ninja import Schema, NinjaAPI
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from ninja.errors import HttpError

from accounts.models import CustomUser
from sites.models import Datastream, Sensor, ObservedProperty, Unit, ThingAssociation

api = NinjaAPI()


@api.post('/token')
def get_token(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    user = authenticate(username=email, password=password)
    if user:
        token = RefreshToken.for_user(user)
        return {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
        }
    else:
        return HttpError(401, 'Invalid credentials')


class CreateUserInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None


@api.post('/users/')
def create_user(request, data: CreateUserInput):
    try:
        user = CustomUser.objects.create_user(
            username=data.email,
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    except Exception as e:
        raise HttpError(400, str(e))
    user.middle_name = data.middle_name
    user.phone = data.phone
    user.address = data.address
    user.save()
    return {'id': user.id, 'username': user.username}


# @router.get('/users/{user_id}', auth=HttpBearer())
# def get_user(request, user_id: int):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         return {
#             'id': user.id,
#             'username': user.username,
#         }
#     except CustomUser.DoesNotExist:
#         return HttpError(404, 'User not found')

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


@api.get("/user/data")
def get_user_data(request):
    try:
        raw_token = request.META['HTTP_AUTHORIZATION'].split()[1]
        decoded_token = UntypedToken(raw_token)
        user_id = decoded_token.payload['user_id']
    except Exception as e:
        return JsonResponse({'detail': 'Invalid or missing token'}, status=401)

    user = CustomUser.objects.get(pk=user_id)
    thing_associations = ThingAssociation.objects.select_related('thing', 'person').prefetch_related('thing__location').filter(person=user)

    owned_things = [
        {
            "id": association.thing.pk,
            "name": association.thing.name,
            "description": association.thing.description,
            "sampling_feature_type": association.thing.sampling_feature_type,
            "sampling_feature_code": association.thing.sampling_feature_code,
            "site_type": association.thing.site_type,
            # "encoding_type": association.thing.location.encoding_type,
            "latitude": association.thing.location.latitude,
            "longitude": association.thing.location.longitude,
            "elevation": association.thing.location.elevation,
            # "elevation_datum": association.thing.location.elevation_datum,
            "city": association.thing.location.city,
            "state": association.thing.location.state,
            "country": association.thing.location.country,
            "is_primary_owner": association.is_primary_owner
        }
        for association in thing_associations if association.owns_thing
    ]

    followed_things = [
        {
            "id": association.thing.pk,
            "name": association.thing.name,
            "description": association.thing.description,
            "sampling_feature_type": association.thing.sampling_feature_type,
            "sampling_feature_code": association.thing.sampling_feature_code,
            "site_type": association.thing.site_type,
            # "encoding_type": association.thing.location.encoding_type,
            "latitude": association.thing.location.latitude,
            "longitude": association.thing.location.longitude,
            "elevation": association.thing.location.elevation,
            # "elevation_datum": association.thing.location.elevation_datum,
            "city": association.thing.location.city,
            "state": association.thing.location.state,
            "country": association.thing.location.country,
        }
        for association in thing_associations if association.follows_thing
    ]

    datastreams = Datastream.objects.filter(thing__associates__person=user).distinct().prefetch_related('unit')
    sensors = Sensor.objects.filter(datastreams__in=datastreams).distinct()
    observed_properties = ObservedProperty.objects.filter(person=user).distinct()
    units = Unit.objects.filter(person=user).distinct()

    response_dict = {
        'owned_things': owned_things,
        'followed_things': followed_things,
        'datastreams': list(datastreams.values()),
        'sensors': list(sensors.values()),
        'observed_properties': list(observed_properties.values()),
        'units': list(units.values())
    }

    return json.dumps(response_dict, cls=CustomEncoder)
