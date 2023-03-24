import datetime
import json
import uuid
from functools import wraps

from _decimal import Decimal
from django.contrib.auth import authenticate, logout
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


class UpdateAccountInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None


@api.put('/user', auth=jwt_auth)
def update_account(request, data: UpdateAccountInput):
    try:
        user = CustomUser.objects.get(pk=request.user_id)
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.email = data.email
        user.username = data.email
        user.middle_name = data.middle_name
        user.phone = data.phone
        user.address = data.address
        user.set_password(data.password)
        user.save()
        return {'detail': 'Your account has been updated!'}
    except CustomUser.DoesNotExist:
        raise HttpError(404, 'User not found')


@api.delete('/user', auth=jwt_auth)
def remove_account(request):
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
    Redirects if not
    """

    @jwt_auth
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        try:
            pk = kwargs.get('pk')
            if not pk:
                datastream = Datastream.objects.get(id=kwargs.get('datastream_pk'))
                pk = datastream.thing.id
        except KeyError:
            datastream = Datastream.objects.get(id=kwargs.get('datastream_pk'))
            pk = datastream.thing.id

        thing = Thing.objects.get(id=pk)
        if not request.user.thing_associations.filter(thing=thing, owns_thing=True).exists():
            raise HttpError(403, 'You do not have permission to access this thing.')

        return func(*args, **kwargs)

    return wrapper


class ThingInput(Schema):
    name: str
    description: str
    sampling_feature_type: str
    sampling_feature_code: str
    site_type: str
    latitude: float
    longitude: float
    elevation: float
    city: str
    state: str
    country: str


@api.post('/things', auth=jwt_auth)
def register_thing(request, data: ThingInput):
    new_thing = Thing.objects.create(name=data.name,
                                     description=data.description,
                                     sampling_feature_type=data.sampling_feature_type,
                                     sampling_feature_code=data.sampling_feature_code,
                                     site_type=data.site_type)

    new_thing.location = Location.objects.create(name='Location for ' + new_thing.name,
                                                 description=new_thing.description,
                                                 encoding_type="application/geo+json",
                                                 latitude=data.latitude,
                                                 longitude=data.longitude,
                                                 elevation=data.elevation,
                                                 city=data.city,
                                                 state=data.state,
                                                 country=data.country,
                                                 thing=new_thing)
    new_thing.save()
    ThingAssociation.objects.create(thing=new_thing, person=request.user, owns_thing=True)
    return {'id': new_thing.id}


@api.get('/things', auth=jwt_auth)
def get_things(request):
    things = Thing.objects.all()
    return [{'id': thing.id, 'name': thing.name, 'description': thing.description} for thing in things]


@api.get('/things/{thing_id}', auth=jwt_auth)
def get_thing(request, thing_id: int):
    thing = Thing.objects.get(id=thing_id)
    return {'id': thing.id, 'name': thing.name, 'description': thing.description}


@api.put('/things/{thing_id}', auth=thing_ownership_required)
def update_thing(request, thing_id: int, data: ThingInput):
    thing = Thing.objects.get(id=thing_id)
    thing.name = data.name
    thing.description = data.description
    thing.sampling_feature_type = data.sampling_feature_type
    thing.sampling_feature_code = data.sampling_feature_code
    thing.site_type = data.site_type
    thing.save()
    return {'detail': 'Thing updated successfully.'}


@api.delete('/things/{thing_id}', auth=thing_ownership_required)
def delete_thing(request, thing_id: int):
    thing = Thing.objects.get(id=thing_id)
    thing.delete()
    return {'detail': 'Thing deleted successfully.'}


class CreateSensorInput(Schema):
    name: str
    description: str
    manufacturer: str
    model: str
    method_type: str
    method_code: str
    method_link: str


@api.post('/sensors', auth=jwt_auth)
def create_sensor(request, data: CreateSensorInput):
    sensor = Sensor.objects.create(
        person=request.user,
        name=data.name,
        description=data.description,
        manufacturer=data.manufacturer,
        model=data.model,
        method_type=data.method_type,
        method_code=data.method_code,
        method_link=data.method_link
    )

    return {'id': sensor.id, 'detail': 'Sensor created successfully.'}


class UpdateSensorInput(Schema):
    name: str
    description: str
    manufacturer: str
    model: str
    method_type: str
    method_code: str
    method_link: str


@api.put('/sensors/{sensor_id}', auth=jwt_auth)
def update_sensor(request, sensor_id: int, data: UpdateSensorInput):
    sensor = Sensor.objects.get(id=sensor_id)

    if request.user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to update this sensor.'}, status=403)

    sensor.name = data.name
    sensor.description = data.description
    sensor.manufacturer = data.manufacturer
    sensor.model = data.model
    sensor.method_type = data.method_type
    sensor.method_code = data.method_code
    sensor.method_link = data.method_link
    sensor.save()

    return {'id': sensor.id, 'detail': 'Sensor updated successfully.'}


@api.delete('/sensors/{sensor_id}', auth=jwt_auth)
def delete_sensor(request, sensor_id: int):
    sensor = Sensor.objects.get(id=sensor_id)

    if request.user != sensor.person:
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


@api.put('/datastreams/{datastream_id}', auth=jwt_auth)
def update_datastream(request, datastream_id: int, data: UpdateDatastreamInput):
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


@api.delete('/datastreams/{datastream_id}', auth=jwt_auth)
def delete_datastream(request, datastream_id: int):
    datastream = Datastream.objects.get(id=datastream_id)

    datastream.delete()

    observations = Observation.objects.filter(datastream=datastream)
    observations.delete()

    return {'detail': 'Datastream deleted successfully.'}

