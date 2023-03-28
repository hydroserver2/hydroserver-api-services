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
from sites.models import Datastream, Sensor, ObservedProperty, Unit, ThingAssociation, Thing, Location, Observation, \
    ProcessingLevel

api = NinjaAPI()


def jwt_auth(request):
    try:
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        request.authenticated_user = user
        return True
    except (KeyError, IndexError, InvalidToken, TokenError):
        raise HttpError(401, 'Unauthorized')


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
    """
    Gets all data related to the user to be cached in the browser
    """
    thing_associations = ThingAssociation.objects.select_related('thing', 'person').prefetch_related(
        'thing__location').filter(person=request.authenticated_user)

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

    user = request.authenticated_user
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
    user = request.authenticated_user

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


@api.delete('/user', auth=jwt_auth)
def delete_user(request):
    try:
        request.authenticated_user.delete()
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
        jwt_auth(request)

        thing_id = kwargs.get('thing_id')
        try:
            thing = Thing.objects.get(id=thing_id)
        except Thing.DoesNotExist:
            raise HttpError(403, 'Site cannot be found')
        if not request.authenticated_user.thing_associations.filter(thing=thing, owns_thing=True).exists():
            raise HttpError(403, 'You do not have permission to access this thing.')

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

        if not request.authenticated_user.thing_associations.filter(thing=thing, owns_thing=True).exists():
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

        ThingAssociation.objects.create(thing=new_thing, person=request.authenticated_user, owns_thing=True)

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
    thing = request.thing

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
    request.thing.delete()
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
    return {'detail': 'Sensor created successfully.', 'id': str(sensor.id)}


@api.put('/sensors/{sensor_id}', auth=jwt_auth)
def update_sensor(request, sensor_id: str, data: SensorInput):
    sensor = Sensor.objects.get(id=sensor_id)
    if request.authenticated_user != sensor.person:
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

    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to delete this sensor.'}, status=403)

    sensor.delete()

    return {'detail': 'Sensor deleted successfully.'}


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
    return {'id': observed_property.id, 'detail': 'Observed Property created successfully.'}


@api.put('/observed-properties/{observed_property_id}', auth=jwt_auth)
def update_observed_property(request, observed_property_id: str, data: ObservedPropertyInput):
    observed_property = ObservedProperty.objects.get(id=observed_property_id)
    if request.authenticated_user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to update this observed property.'}, status=403)

    if data.name:
        observed_property.name = data.name
    if data.definition:
        observed_property.definition = data.definition
    if data.description:
        observed_property.description = data.description
    if data.variable_type:
        observed_property.variable_type = data.variable_type
    if data.variable_code:
        observed_property.variable_code = data.variable_code

    observed_property.save()

    return {'id': observed_property.id, 'detail': 'Observed Property updated successfully.'}


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
    unit: str = None
    thing_id: str
    sensor: str
    observed_property: str
    processing_level: str = None

    name: str
    description: str = None
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


@api.post('/datastreams', auth=jwt_auth)
def create_datastream(request, data: CreateDatastreamInput):
    # Should only be able to create a datastream for a thing they own
    try:
        thing = Thing.objects.get(id=data.thing_id)
    except Thing.DoesNotExist:
        return JsonResponse({'detail': 'Thing not found.'}, status=404)

    try:
        sensor = Sensor.objects.get(id=data.sensor)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    try:
        observed_property = ObservedProperty.objects.get(id=data.observed_property)
    except ObservedProperty.DoesNotExist:
        return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    try:
        unit = Unit.objects.get(id=data.unit) if data.unit else None
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if data.processing_level:
        processing_level = ProcessingLevel.objects.get(id=data.processing_level)
    else:
        processing_level = None

    datastream = Datastream.objects.create(
        name=data.name,
        description=data.description,
        observed_property=observed_property,
        unit=unit,
        processing_level=processing_level,
        sampled_medium=data.sampled_medium,
        status=data.status,
        no_data_value=data.no_data_value,
        aggregation_statistic=data.aggregation_statistic,
        result_type=data.result_type if data.result_type else 'Time Series Coverage',
        observation_type=data.observation_type if data.observation_type else 'OM_Measurement',
        thing=thing,
        sensor=sensor,
    )

    return {'id': datastream.id, 'detail': 'Datastream created successfully.'}


class UpdateDatastreamInput(Schema):
    unit: str = None
    sensor: str = None
    observed_property: str = None
    processing_level: str = None

    name: str = None
    description: str = None
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


@api.put('/datastreams/{datastream_id}', auth=jwt_auth)
@datastream_ownership_required
def update_datastream(request, datastream_id: str, data: UpdateDatastreamInput):
    with transaction.atomic():
        datastream = request.datastream

        if data.sensor:
            try:
                datastream.sensor = Sensor.objects.get(id=data.sensor)
            except Sensor.DoesNotExist:
                return JsonResponse({'detail': 'Sensor not found.'}, status=404)

        if data.observed_property:
            try:
                datastream.observed_property = ObservedProperty.objects.get(id=data.observed_property)
            except ObservedProperty.DoesNotExist:
                return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

        if data.unit:
            try:
                datastream.unit = Unit.objects.get(id=data.unit)
            except Unit.DoesNotExist:
                return JsonResponse({'detail': 'Unit not found.'}, status=404)

        if data.processing_level:
            try:
                datastream.processing_level = ProcessingLevel.objects.get(id=data.processing_level)
            except ProcessingLevel.DoesNotExist:
                return JsonResponse({'detail': 'Processing Level not found.'}, status=404)

        if data.name:
            datastream.name = data.name
        if data.description:
            datastream.description = data.description
        if data.observation_type:
            datastream.observation_type = data.observation_type
        if data.result_type:
            datastream.result_type = data.result_type
        if data.status:
            datastream.status = data.status
        if data.sampled_medium:
            datastream.sampled_medium = data.sampled_medium
        if data.no_data_value:
            datastream.no_data_value = data.no_data_value
        if data.aggregation_statistic:
            datastream.aggregation_statistic = data.aggregation_statistic
        if data.time_aggregation_interval:
            datastream.time_aggregation_interval = data.time_aggregation_interval
        if data.time_aggregation_interval_units:
            try:
                datastream.time_aggregation_interval_units = Unit.objects.get(id=data.time_aggregation_interval_units)
            except Unit.DoesNotExist:
                return JsonResponse({'detail': 'time_aggregation_interval_units not found.'}, status=404)
        if data.phenomenon_start_time:
            datastream.phenomenon_start_time = data.phenomenon_start_time
        if data.phenomenon_end_time:
            datastream.phenomenon_end_time = data.phenomenon_end_time
        if data.result_begin_time:
            datastream.result_begin_time = data.result_begin_time
        if data.result_end_time:
            datastream.result_end_time = data.result_end_time
        if data.value_count:
            datastream.value_count = data.value_count
        if data.intended_time_spacing:
            datastream.intended_time_spacing = data.intended_time_spacing
        if data.intended_time_spacing_units:
            try:
                datastream.intended_time_spacing_units = Unit.objects.get(id=data.intended_time_spacing_units)
            except Unit.DoesNotExist:
                return JsonResponse({'detail': 'intended_time_spacing_units not found.'}, status=404)

        datastream.save()

    return {'id': datastream.id, 'detail': 'Datastream updated successfully.'}


@api.delete('/datastreams/{datastream_id}')
@datastream_ownership_required
def delete_datastream(request, datastream_id: str):
    datastream = request.datastream
    observations = Observation.objects.filter(datastream=datastream)
    if observations.exists():
        observations.delete()

    datastream.delete()

    observations = Observation.objects.filter(datastream=datastream)
    observations.delete()

    return {'detail': 'Datastream deleted successfully.'}


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
    return {'id': unit.id, 'detail': 'Unit created successfully.'}


class UpdateUnitInput(Schema):
    name: str
    symbol:  str
    definition: str
    unit_type: str


@api.put('/units/{unit_id}', auth=jwt_auth)
def update_unit(request, unit_id: str, data: UpdateUnitInput):
    unit = Unit.objects.get(id=unit_id)
    if request.authenticated_user != unit.person:
        return JsonResponse({'detail': 'You are not authorized to update this unit.'}, status=403)

    if data.name:
        unit.name = data.name
    if data.symbol:
        unit.symbol = data.symbol
    if data.definition:
        unit.definition = data.definition
    if data.unit_type:
        unit.unit_type = data.unit_type

    unit.save()
    return {'detail': 'Unit updated successfully.'}


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
