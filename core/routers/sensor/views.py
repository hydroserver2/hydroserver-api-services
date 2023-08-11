from ninja import Router
from typing import List
from django.http import HttpRequest
from django.db import transaction
from django.db.models import Q
from core.auth import BasicAuth, JWTAuth
from core.routers.sensor.schemas import *
from sites.models import Sensor


router = Router(tags=['Sensors'])


@router.get(
    '/sensors',
    auth=[BasicAuth(), JWTAuth()],
    response={200: List[SensorGetResponse]}
)
def get_sensors(
        request: HttpRequest,
        # params: SensorQueryParams = Query(...)
):
    """
    Returns a list of sensor records.

    Details for all sensor records owned by an authenticated user will be returned in the response. No records will
    be returned for unauthenticated requests.
    """

    sensors = Sensor.objects.filter(Q(person=getattr(request, 'authenticated_user', None)))

    return 200, sensors


@router.post(
    '/sensors',
    auth=[BasicAuth(), JWTAuth()],
    response={201: SensorGetResponse}
)
@transaction.atomic
def create_sensor(
        request: HttpRequest,
        data: SensorPostBody
):
    """
    Creates a new sensor record.

    The created record will be owned by the authenticated user who made the request. If the sensor record was created
    successfully, the response will contain details for the created record.
    """

    sensor = Sensor.objects.create(
        person=getattr(request, 'authenticated_user'),
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

    return 201, sensor


@router.get(
    '/sensors/{sensor_id}',
    auth=[BasicAuth(), JWTAuth()],
    response={200: SensorGetResponse, 404: None}
)
def get_sensor(
        request: HttpRequest,
        sensor_id: UUID
):
    """
    Gets a single sensor record.

    Details for a single sensor record identified by the given sensor ID and owned by the authenticated user will be
    returned in the response.
    """

    sensors = Sensor.objects.filter(Q(person=getattr(request, 'authenticated_user', None))).filter(id=sensor_id)

    if not sensors:
        return 404, None

    return 200, sensors[0]


@router.patch(
    '/sensors/{sensor_id}',
    auth=[BasicAuth(), JWTAuth()],
    response={203: SensorGetResponse, 404: None}
)
@transaction.atomic
def update_sensor(
        request: HttpRequest,
        sensor_id: UUID,
        data: SensorPatchBody
):
    """
    Updates an existing sensor record.

    The record associated with the given sensor ID must be owned by the authenticated user who made the request. If the
    sensor record was updated successfully, the response will contain details for the updated record.
    """

    sensor = Sensor.objects.get(id=sensor_id)

    if not sensor:
        return 404, None

    if sensor.person != getattr(request, 'authenticated_user', None):
        return 404, None

    data_dict = data.dict(exclude_unset=True)

    for field in [
        'name', 'description', 'encoding_type', 'manufacturer', 'model', 'model_url', 'method_type', 'method_link',
        'method_code'
    ]:
        if field in data_dict:
            setattr(sensor, field, data_dict[field])

    sensor.save()

    return 203, sensor


@router.delete(
    '/sensors/{sensor_id}',
    auth=[BasicAuth(), JWTAuth()],
    response={200: None, 404: None, 403: None, 500: None}
)
def delete_sensor(
        request: HttpRequest,
        sensor_id: UUID
):
    """
    Deletes an existing sensor record.

    The record associated with the given sensor ID must be owned by the authenticated user who made the request.
    """

    sensor = Sensor.objects.get(id=sensor_id)

    if not sensor:
        return 404, None

    if sensor.person != getattr(request, 'authenticated_user', None):
        return 403, None

    try:
        sensor.delete()
    except Exception as e:
        return 500, str(e)

    return 200, 'Sensor deleted successfully.'
