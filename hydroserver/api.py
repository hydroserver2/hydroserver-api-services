import datetime
import json
import uuid
from functools import wraps

from _decimal import Decimal
from django.contrib.auth import authenticate, logout
from django.db import transaction
from django.http import JsonResponse
from ninja import Schema, NinjaAPI
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from ninja.errors import HttpError

from accounts.models import CustomUser
from sites.models import Datastream, Sensor, ObservedProperty, Unit, ThingAssociation, Thing, Location, Observation

api = NinjaAPI()


def jwt_auth(request):
    try:
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        request.user_id = user_id
        return True
    except (KeyError, IndexError, InvalidToken, TokenError):
        return False


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
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)


class CreateUserInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None


@api.post('/user')
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


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


@api.get("/user/data", auth=jwt_auth)
def get_user_data(request):
    user = CustomUser.objects.get(pk=request.user_id)
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

    user_dict = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "address": user.address,
        "organization": user.organization,
    }

    datastreams = Datastream.objects.filter(thing__associates__person=user).distinct().prefetch_related('unit')
    sensors = Sensor.objects.filter(datastreams__in=datastreams).distinct()
    observed_properties = ObservedProperty.objects.filter(person=user).distinct()
    units = Unit.objects.filter(person=user).distinct()

    return json.dumps({
        'user': user_dict,
        'owned_things': owned_things,
        'followed_things': followed_things,
        'datastreams': list(datastreams.values()),
        'sensors': list(sensors.values()),
        'observed_properties': list(observed_properties.values()),
        'units': list(units.values())
    }, cls=CustomEncoder)


class UpdateUserInput(Schema):
    first_name: str = None
    last_name: str = None
    email: str = None
    password: str = None
    middle_name: str = None
    phone: str = None
    address: str = None


@api.put('/user', auth=jwt_auth)
def update_user(request, data: UpdateUserInput):
    try:
        user = CustomUser.objects.get(pk=request.user_id)

        if data.first_name:
            user.first_name = data.first_name
        if data.last_name:
            user.last_name = data.last_name
        if data.email:
            user.email = data.email
            user.username = data.email
        if data.middle_name:
            user.middle_name = data.middle_name
        if data.phone:
            user.phone = data.phone
        if data.address:
            user.address = data.address
        if data.password:
            user.set_password(data.password)

        user.save()
        return {'detail': 'Your account has been updated!'}
    except CustomUser.DoesNotExist:
        raise HttpError(404, 'User not found')


@api.delete('/user', auth=jwt_auth)
def delete_user(request):
    try:
        user = CustomUser.objects.get(pk=request.user_id)
        user.delete()
        logout(request)
        return {'detail': 'Your account has been removed!'}
    except CustomUser.DoesNotExist:
        raise HttpError(404, 'User not found')


def thing_ownership_required(func):
    """
    Decorator for thing views that checks the user is logged in and is an owner of the related thing.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        jwt_auth_result = jwt_auth(request)
        if not jwt_auth_result:
            raise HttpError(401, 'Unauthorized')

        thing_id = kwargs.get('thing_id')
        user = CustomUser.objects.get(pk=request.user_id)
        thing = Thing.objects.get(id=thing_id)

        if not user.thing_associations.filter(thing=thing, owns_thing=True).exists():
            raise HttpError(403, 'You do not have permission to access this thing.')

        return func(request, *args, **kwargs)

    return wrapper


def datastream_ownership_required(func):
    """
    Decorator for datastream views that checks the user is logged in and is an owner of the related datastream's thing.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        jwt_auth_result = jwt_auth(request)
        if not jwt_auth_result:
            raise HttpError(401, 'Unauthorized')

        datastream_id = kwargs.get('datastream_id')
        user = CustomUser.objects.get(pk=request.user_id)
        datastream = Datastream.objects.get(id=datastream_id)
        thing = datastream.thing

        if not user.thing_associations.filter(thing=thing, owns_thing=True).exists():
            raise HttpError(403, 'You do not have permission to access this datastream.')

        return func(request, *args, **kwargs)

    return wrapper


class ThingInput(Schema):
    name: str
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    latitude: float
    longitude: float
    elevation: float
    city: str = None
    state: str = None
    country: str = None


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
                                city=data.city, state=data.state, country=data.country,
                                thing=new_thing)

        user = CustomUser.objects.get(pk=request.user_id)
        ThingAssociation.objects.create(thing=new_thing, person=user, owns_thing=True)

    return {'id': new_thing.id}


@api.get('/things')
def get_things(request):
    things = Thing.objects.all()

    return [
        {
            "id": thing.pk,
            "name": thing.name,
            "description": thing.description,
            "sampling_feature_type": thing.sampling_feature_type,
            "sampling_feature_code": thing.sampling_feature_code,
            "site_type": thing.site_type,
            # "encoding_type": association.thing.location.encoding_type,
            "latitude": thing.location.latitude,
            "longitude": thing.location.longitude,
            "elevation": thing.location.elevation,
            # "elevation_datum": association.thing.location.elevation_datum,
            "city": thing.location.city,
            "state": thing.location.state,
            "country": thing.location.country
        } for thing in things]


@api.get('/things/{thing_id}', auth=jwt_auth)
def get_thing(request, thing_id: str):
    thing = Thing.objects.get(id=thing_id)
    return {
        "id": thing.pk,
        "name": thing.name,
        "description": thing.description,
        "sampling_feature_type": thing.sampling_feature_type,
        "sampling_feature_code": thing.sampling_feature_code,
        "site_type": thing.site_type,
        # "encoding_type": association.thing.location.encoding_type,
        "latitude": thing.location.latitude,
        "longitude": thing.location.longitude,
        "elevation": thing.location.elevation,
        # "elevation_datum": association.thing.location.elevation_datum,
        "city": thing.location.city,
        "state": thing.location.state,
        "country": thing.location.country}


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
    country: str = None


@api.put('/things/{thing_id}')
@thing_ownership_required
def update_thing(request, thing_id: str, data: UpdateThingInput):
    thing = Thing.objects.get(id=thing_id)

    if data.name:
        thing.name = data.name
    if data.description:
        thing.description = data.description
    if data.sampling_feature_type:
        thing.sampling_feature_type = data.sampling_feature_type
    if data.sampling_feature_code:
        thing.sampling_feature_code = data.sampling_feature_code
    if data.site_type:
        thing.site_type = data.site_type

    thing.save()
    return {'detail': 'Thing updated successfully.'}


@api.delete('/things/{thing_id}')
@thing_ownership_required
def delete_thing(request, thing_id: str):
    try:
        thing = Thing.objects.get(id=thing_id)
    except Thing.DoesNotExist:
        return {'detail': 'Thing does not exist'}
    thing.delete()

    return {'detail': 'Thing deleted successfully.'}


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
    user = CustomUser.objects.get(pk=request.user_id)
    sensor = Sensor(
        person=user,
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
    sensor.save()
    return {'detail': 'Sensor created successfully.', 'id': str(sensor.id)}


@api.put('/sensors/{sensor_id}', auth=jwt_auth)
def update_sensor(request, sensor_id: str, data: SensorInput):
    sensor = Sensor.objects.get(id=sensor_id)
    user = CustomUser.objects.get(pk=request.user_id)
    if user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to update this sensor.'}, status=403)

    if data.name:
        sensor.name = data.name
    if data.description:
        sensor.description = data.description
    if data.manufacturer:
        sensor.manufacturer = data.manufacturer
    if data.model:
        sensor.model = data.model
    if data.method_type:
        sensor.method_type = data.method_type
    if data.method_code:
        sensor.method_code = data.method_code
    if data.method_link:
        sensor.method_link = data.method_link
    if data.encoding_type:
        sensor.encoding_type = data.encoding_type
    if data.model_url:
        sensor.model_url = data.model_url

    sensor.save()

    return {'id': sensor.id, 'detail': 'Sensor updated successfully.'}


@api.delete('/sensors/{sensor_id}', auth=jwt_auth)
def delete_sensor(request, sensor_id: str):
    try:
        sensor = Sensor.objects.get(id=sensor_id)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    user = CustomUser.objects.get(pk=request.user_id)
    if user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to delete this sensor.'}, status=403)

    sensor.delete()

    return {'detail': 'Sensor deleted successfully.'}


class CreateObservedPropertyInput(Schema):
    name: str
    definition: str
    description: str


@api.post('/observed-properties', auth=jwt_auth)
def create_observed_property(request, data: CreateObservedPropertyInput):
    observed_property, created = ObservedProperty.objects.get_or_create(
        name=data.name,
        person=request.user,
        definition=data.definition,
        description=data.description
    )

    if created:
        return {'id': observed_property.id, 'detail': 'Observed Property created successfully.'}
    else:
        return {'detail': 'Observed Property already exists.'}


class UpdateObservedPropertyInput(Schema):
    name: str
    definition: str
    description: str


@api.put('/observed-properties/{observed_property_id}', auth=jwt_auth)
def update_observed_property(request, observed_property_id: int, data: UpdateObservedPropertyInput):
    observed_property = ObservedProperty.objects.get(id=observed_property_id)

    if request.user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to update this observed property.'}, status=403)

    observed_property.name = data.name
    observed_property.definition = data.definition
    observed_property.description = data.description
    observed_property.save()

    return {'id': observed_property.id, 'detail': 'Observed Property updated successfully.'}


@api.delete('/observed-properties/{observed_property_id}', auth=jwt_auth)
def delete_observed_property(request, observed_property_id: int):
    observed_property = ObservedProperty.objects.get(id=observed_property_id)

    if request.user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to delete this observed property.'}, status=403)

    observed_property.delete()

    return {'detail': 'Observed Property deleted successfully.'}


class CreateDatastreamInput(Schema):
    thing_id: int
    method: int
    observed_property: int
    unit: int
    processing_level: int
    sampled_medium: str
    status: str
    no_data_value: float
    aggregation_statistic: str


@api.post('/datastreams', auth=jwt_auth)
def create_datastream(request, data: CreateDatastreamInput):
    thing = Thing.objects.get(id=data.thing_id)
    sensor = Sensor.objects.get(id=data.method)
    observed_property = ObservedProperty.objects.get(id=data.observed_property)
    unit = Unit.objects.get(id=data.unit)

    datastream = Datastream.objects.create(
        name=str(sensor),
        description='description',
        observed_property=observed_property,
        unit=unit,
        processing_level=data.processing_level,
        sampled_medium=data.sampled_medium,
        status=data.status,
        no_data_value=data.no_data_value,
        aggregation_statistic=data.aggregation_statistic,
        result_type='Time Series Coverage',
        observation_type='OM_Measurement',
        thing=thing,
        sensor=sensor,
    )

    return {'id': datastream.id, 'detail': 'Datastream created successfully.'}


class UpdateDatastreamInput(Schema):
    method: int
    observed_property: int
    unit: int
    processing_level: int
    sampled_medium: str
    status: str
    no_data_value: float
    aggregation_statistic: str


@api.put('/datastreams/{datastream_id}')
@datastream_ownership_required
def update_datastream(request, datastream_id: str, data: UpdateDatastreamInput):
    datastream = Datastream.objects.get(id=datastream_id)

    sensor = Sensor.objects.get(id=data.method)
    observed_property = ObservedProperty.objects.get(id=data.observed_property)
    unit = Unit.objects.get(id=data.unit)

    datastream.sensor = sensor
    datastream.observed_property = observed_property
    datastream.unit = unit
    datastream.processing_level = data.processing_level
    datastream.sampled_medium = data.sampled_medium
    datastream.status = data.status
    datastream.no_data_value = data.no_data_value
    datastream.aggregation_statistic = data.aggregation_statistic

    datastream.save()

    return {'id': datastream.id, 'detail': 'Datastream updated successfully.'}


@api.delete('/datastreams/{datastream_id}')
@datastream_ownership_required
def delete_datastream(request, datastream_id: str):
    datastream = Datastream.objects.get(id=datastream_id)

    datastream.delete()

    observations = Observation.objects.filter(datastream=datastream)
    observations.delete()

    return {'detail': 'Datastream deleted successfully.'}

