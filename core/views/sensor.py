from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import Sensor
from core.schemas.metadata import metadataOwnerOptions
from core.schemas.sensor import SensorGetResponse, SensorPostBody, SensorPatchBody, SensorFields


router = DataManagementRouter(tags=['Sensors'])


@router.dm_list('', response=SensorGetResponse)
def get_sensors(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
    """
    Get a list of Sensors

    This endpoint returns a list of sensors owned by the authenticated user.
    """

    sensor_query = Sensor.objects.select_related('person')
    sensor_query = sensor_query.filter(Q(person__isnull=True) | Q(person__is_active=True))

    if owner == 'currentUser':
        sensor_query = sensor_query.filter(Q(person__isnull=False) & Q(person=request.authenticated_user))
    elif owner == 'noUser':
        sensor_query = sensor_query.filter(person__isnull=True)
    elif owner == 'currentUserOrNoUser':
        sensor_query = sensor_query.filter(Q(person__isnull=True) | Q(person=request.authenticated_user))
    elif owner == 'anyUser':
        sensor_query = sensor_query.filter(person__isnull=False)

    sensor_query = sensor_query.distinct()

    response = [
        sensor for sensor in sensor_query.all()
    ]

    return 200, response


@router.dm_get('{sensor_id}', response=SensorGetResponse)
def get_sensor(request, sensor_id: UUID = Path(...)):
    """
    Get details for a Sensor

    This endpoint returns details for a sensor given a sensor ID.
    """

    sensor = Sensor.objects.get_by_id(
        sensor_id=sensor_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, sensor


@router.dm_post('', response=SensorGetResponse)
@transaction.atomic
def create_sensor(request, data: SensorPostBody):
    """
    Create a Sensor

    This endpoint will create a new sensor owned by the authenticated user and returns the created sensor.
    """

    sensor = Sensor.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(SensorFields.model_fields.keys()))
    )

    return 201, sensor


@router.dm_patch('{sensor_id}', response=SensorGetResponse)
@transaction.atomic
def update_sensor(request, data: SensorPatchBody, sensor_id: UUID = Path(...)):
    """
    Update a Sensor

    This endpoint will update an existing sensor owned by the authenticated user and return the updated sensor.
    """

    sensor = Sensor.objects.get_by_id(
        sensor_id=sensor_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )
    sensor_data = data.dict(include=set(SensorFields.model_fields.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'Sensor', fields=[*sensor_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this sensor.'

    for field, value in sensor_data.items():
        setattr(sensor, field, value)

    sensor.save()

    return 203, sensor


@router.dm_delete('{sensor_id}')
@transaction.atomic
def delete_sensor(request, sensor_id: UUID = Path(...)):
    """
    Delete a Sensor

    This endpoint will delete an existing sensor if the authenticated user is the primary owner of the sensor.
    """

    sensor = Sensor.objects.get_by_id(
        sensor_id=sensor_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        sensor.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
