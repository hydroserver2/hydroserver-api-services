from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from core.router import DataManagementRouter
from core.models import Sensor
from core.schemas_old import metadataOwnerOptions
from .schemas import SensorGetResponse, SensorPostBody, SensorPatchBody, SensorFields
from .utils import query_sensors, get_sensor_by_id, build_sensor_response


router = DataManagementRouter(tags=['Sensors'])


@router.dm_list('', response=SensorGetResponse)
def get_sensors(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
    """
    Get a list of Sensors

    This endpoint returns a list of Sensors owned by the authenticated user.
    """

    # return Sensor.endpoints.list(user=request.authenticated_user)

    sensor_query, _ = query_sensors(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=True if owner == 'currentUser' else False,
        require_ownership_or_unowned=True if owner == 'currentUserOrNoUser' else False,
        raise_http_errors=False
    )

    return [
        build_sensor_response(sensor) for sensor in sensor_query.all()
        if owner in ['currentUser', 'currentUserOrNoUser', 'anyUserOrNoUser']
        or (owner == 'noUser' and sensor.person is None)
        or (owner == 'anyUser' and sensor.person is not None)
    ]


@router.dm_get('{sensor_id}', response=SensorGetResponse)
def get_sensor(request, sensor_id: UUID = Path(...)):
    """
    Get details for a Sensor

    This endpoint returns details for a Sensor given a Sensor ID.
    """

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor_id, raise_http_errors=True)

    return 200, build_sensor_response(sensor)


@router.dm_post('', response=SensorGetResponse)
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

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor.id, raise_http_errors=True)

    return 201, build_sensor_response(sensor)


@router.dm_patch('{sensor_id}', response=SensorGetResponse)
@transaction.atomic
def update_sensor(request, data: SensorPatchBody, sensor_id: UUID = Path(...)):
    """
    Update a Sensor

    This endpoint will update an existing Sensor owned by the authenticated user and return the updated Sensor.
    """

    sensor = get_sensor_by_id(
        user=request.authenticated_user,
        sensor_id=sensor_id,
        require_ownership=True,
        raise_http_errors=True
    )

    sensor_data = data.dict(include=set(SensorFields.__fields__.keys()), exclude_unset=True)

    for field, value in sensor_data.items():
        setattr(sensor, field, value)

    sensor.save()

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor_id)

    return 203, build_sensor_response(sensor)


@router.dm_delete('{sensor_id}')
@transaction.atomic
def delete_sensor(request, sensor_id: UUID = Path(...)):
    """
    Delete a Sensor

    This endpoint will delete an existing Sensor if the authenticated user is the primary owner of the Sensor.
    """

    sensor = get_sensor_by_id(
        user=request.authenticated_user,
        sensor_id=sensor_id,
        require_ownership=True,
        raise_http_errors=True
    )

    try:
        sensor.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
