from ninja import Router
from typing import List
from uuid import UUID
from django.db import transaction
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import Sensor
from .schemas import SensorGetResponse, SensorPostBody, SensorPatchBody, SensorFields
from .utils import query_sensors, get_sensor_by_id


router = Router(tags=['Sensors'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[SensorGetResponse]
    },
    by_alias=True
)
def get_sensors(request):
    """
    Get a list of Sensors

    This endpoint returns a list of Sensors owned by the authenticated user.
    """

    sensors = query_sensors(
        user=getattr(request, 'authenticated_user', None)
    )

    return sensors


@router.get(
    '{sensor_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: SensorGetResponse,
        404: str
    },
    by_alias=True
)
def get_sensor(request, sensor_id: UUID):
    """
    Get details for a Sensor

    This endpoint returns details for a Sensor given a Sensor ID.
    """

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor_id)

    if not sensor:
        return 404, f'Sensor with ID: {sensor_id} was not found.'

    return 200, sensor


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: SensorGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def create_sensor(request, data: SensorPostBody):
    """
    Create a Sensor

    This endpoint will create a new Sensor owned by the authenticated user and returns the created Sensor.
    """

    sensor = Sensor.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(SensorFields.__fields__.keys()))
    )

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor.id)

    if not sensor:
        return 500, 'Encountered an unexpected error creating Sensor.'

    return 201, sensor


@router.patch(
    '{sensor_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: SensorGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_sensor(request, sensor_id: UUID, data: SensorPatchBody):
    """
    Update a Sensor

    This endpoint will update an existing Sensor owned by the authenticated user and return the updated Sensor.
    """

    sensor = Sensor.objects.select_related('person').get(pk=sensor_id)

    if not sensor:
        return 404, f'Sensor with ID: {sensor_id} was not found.'

    if sensor.person != request.authenticated_user:
        return 403, 'You do not have permission to modify this Sensor.'

    sensor_data = data.dict(include=set(SensorFields.__fields__.keys()), exclude_unset=True)

    for field, value in sensor_data.items():
        setattr(sensor, field, value)

    sensor.save()

    sensor_response = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor.id)

    if not sensor_response:
        return 500, 'Encountered an unexpected error updating Sensor.'

    return 203, sensor_response


@router.delete(
    '{sensor_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        500: str
    }
)
@transaction.atomic
def delete_sensor(request, sensor_id: UUID):
    """
    Delete a Sensor

    This endpoint will delete an existing Sensor if the authenticated user is the primary owner of the Sensor.
    """

    sensor = Sensor.objects.select_related('person').get(pk=sensor_id)

    if not sensor:
        return 404, f'Sensor with ID: {sensor_id} was not found.'

    if sensor.person != request.authenticated_user:
        return 403, 'You do not have permission to delete this Sensor.'

    try:
        sensor.delete()
    except Exception as e:
        return 500, str(e)

    return 204, None
