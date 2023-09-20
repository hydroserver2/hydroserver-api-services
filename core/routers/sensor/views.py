from ninja import Router, Path
from typing import List
from uuid import UUID
from django.db import transaction, IntegrityError
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import Sensor
from .schemas import SensorGetResponse, SensorPostBody, SensorPatchBody, SensorFields
from .utils import query_sensors, get_sensor_by_id, build_sensor_response


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

    sensor_query, _ = query_sensors(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    return [
        build_sensor_response(sensor) for sensor in sensor_query.all()
    ]


@router.get(
    '{sensor_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: SensorGetResponse,
        404: str
    },
    by_alias=True
)
def get_sensor(request, sensor_id: UUID = Path(...)):
    """
    Get details for a Sensor

    This endpoint returns details for a Sensor given a Sensor ID.
    """

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor_id, raise_http_errors=True)

    return 200, build_sensor_response(sensor)


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

    sensor = get_sensor_by_id(user=request.authenticated_user, sensor_id=sensor.id, raise_http_errors=True)

    return 201, build_sensor_response(sensor)


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


@router.delete(
    '{sensor_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        409: str
    }
)
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
