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
    """"""

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
    """"""

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
def get_sensors(
        request: HttpRequest,
        sensor_id: UUID
):
    """"""

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
    """"""

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
    response={200: None, 404: None, 403: None}
)
def delete_sensor(
        request: HttpRequest,
        sensor_id: UUID
):
    """"""

    try:
        sensor = Sensor.objects.get(id=sensor_id)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to delete this sensor.'}, status=403)

    sensor.delete()

    return {'detail': 'Sensor deleted successfully.'}
