import copy
import uuid
from functools import wraps
from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from ninja.errors import HttpError
from accounts.models import CustomUser
from hydroserver.schemas import *
from sites.models import Datastream, Sensor, ObservedProperty, Unit, ThingAssociation, Thing, Observation, \
    ProcessingLevel

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


def get_public_datastreams(thing_id: str):
    try:
        thing = Thing.objects.get(pk=thing_id)
    except Thing.DoesNotExist:
        return JsonResponse({'detail': 'Site not found.'}, status=404)
    return JsonResponse([
        datastream_to_dict(datastream) 
        for datastream in thing.datastreams.all() if datastream.is_visible], safe=False)


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


def observed_property_to_dict(observed_property):
    return {
        "id": observed_property.pk,
        "name": observed_property.name,
        "definition": observed_property.definition,
        "description": observed_property.description,
        "variable_type": observed_property.variable_type,
        "variable_code": observed_property.variable_code,
    }


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


def unit_to_dict(unit):
    return {
        "id": unit.pk,
        "name": unit.name,
        "symbol": unit.symbol,
        "definition": unit.definition,
        "unit_type": unit.unit_type,
        "person_id": unit.person.pk if unit.person else None
    }


def processing_level_to_dict(processing_level):
    return {
        "id": processing_level.pk,
        "processing_level_code": processing_level.processing_level_code,
        "definition": processing_level.definition,
        "explanation": processing_level.explanation,
        "person_id": processing_level.person.pk if processing_level.person else None
    }

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
            HydroLoaderConfFileDatastream(
                datastream_id=datastream.id,
                column=datastream.data_source_column
            ) for datastream in data_source.datastream_set.all()
        ]
    )