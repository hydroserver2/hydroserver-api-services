import copy
import uuid
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, Sensor
from .schemas import SensorFields


def apply_sensor_auth_rules(
        user: Optional[Person],
        sensor_query: QuerySet,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = sensor_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Sensor.')

    if user and require_ownership is True:
        sensor_query = sensor_query.filter((Q(person=user) & Q(person__is_active=True)))
    elif user and require_ownership_or_unowned is True:
        sensor_query = sensor_query.filter((Q(person=user) & Q(person__is_active=True)) | Q(person=None))
    elif not user and require_ownership_or_unowned is True:
        sensor_query = sensor_query.filter((Q(person=user) & Q(person__is_active=True)))

    return sensor_query, result_exists


def query_sensors(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        sensor_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    sensor_query = Sensor.objects

    if sensor_ids:
        sensor_query = sensor_query.filter(id__in=sensor_ids)

    if datastream_ids:
        sensor_query = sensor_query.filter(datastreams__id__in=datastream_ids)

    sensor_query = sensor_query.select_related('person', 'person__organization')

    sensor_query, result_exists = apply_sensor_auth_rules(
        user=user,
        sensor_query=sensor_query,
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result=check_result_exists
    )

    return sensor_query, result_exists


def check_sensor_by_id(
        user: Optional[Person],
        sensor_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    sensor_query, sensor_exists = query_sensors(
        user=user,
        sensor_ids=[sensor_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    sensor = sensor_query.exists()

    if raise_http_errors and not sensor_exists:
        raise HttpError(404, 'Sensor not found.')
    if raise_http_errors and sensor_exists and not sensor:
        raise HttpError(403, 'You do not have permission to perform this action on this Sensor.')

    return sensor


def get_sensor_by_id(
        user: Optional[Person],
        sensor_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    sensor_query, sensor_exists = query_sensors(
        user=user,
        sensor_ids=[sensor_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    sensor = next(iter(sensor_query.all()), None)

    if raise_http_errors and not sensor_exists:
        raise HttpError(404, 'Sensor not found.')
    if raise_http_errors and sensor_exists and not sensor:
        raise HttpError(403, 'You do not have permission to perform this action on this Sensor.')

    return sensor


def build_sensor_response(sensor):
    return {
        'id': sensor.id,
        'owner': sensor.person.email if sensor.person else None,
        **{field: getattr(sensor, field) for field in SensorFields.__fields__.keys()},
    }


def transfer_sensor_ownership(datastream, new_owner, old_owner):

    if datastream.sensor.person != old_owner or datastream.sensor.person is None:
        return

    fields_to_compare = ['name', 'description', 'encoding_type', 'manufacturer', 'model', 'model_link',
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
