from django.db.models import Q
from django.http import JsonResponse
from ninja import Router, Schema
from pydantic import Field
from core.models import Sensor
from core.utils.authentication import jwt_auth
from core.utils.sensor import sensor_to_dict
from sensorthings.validators import allow_partial

router = Router(tags=['Sensors'])


class SensorFields(Schema):
    name: str = None
    description: str
    encoding_type: str = Field(alias="encodingType")
    manufacturer: str = None
    model: str = None
    model_link: str = Field(None, alias='modelLink')
    method_type: str = Field(alias='methodType')
    method_link: str = Field(None, alias='methodLink')
    method_code: str = Field(None, alias='methodCode')


class SensorPostBody(SensorFields):
    pass


@allow_partial
class SensorPatchBody(SensorFields):
    pass


@router.post('', auth=jwt_auth)
def create_sensor(request, data: SensorFields):
    sensor_data = data.dict(include=set(SensorFields.__fields__.keys()))
    sensor = Sensor.objects.create(person=request.authenticated_user, **sensor_data)
    return JsonResponse(sensor_to_dict(sensor))


@router.get('', auth=jwt_auth)
def get_sensors(request):
    sensors = Sensor.objects.filter(Q(person=request.authenticated_user))
    return JsonResponse([sensor_to_dict(sensor) for sensor in sensors], safe=False)


@router.patch('/{sensor_id}', auth=jwt_auth)
def update_sensor(request, sensor_id: str, data: SensorPatchBody):
    sensor = Sensor.objects.get(id=sensor_id)
    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to update this sensor.'}, status=403)

    sensor_data = data.dict(exclude_unset=True)
    for key, value in sensor_data.items():
        setattr(sensor, key, value)

    sensor.save()

    return JsonResponse(sensor_to_dict(sensor))


@router.delete('/{sensor_id}', auth=jwt_auth)
def delete_sensor(request, sensor_id: str):
    try:
        sensor = Sensor.objects.get(id=sensor_id)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to delete this sensor.'}, status=403)

    sensor.delete()

    return {'detail': 'Sensor deleted successfully.'}
