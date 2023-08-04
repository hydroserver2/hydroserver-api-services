from hydroserver.api.api import api
from django.db.models import Q
from django.http import JsonResponse
from hydroserver.api.util import jwt_auth, sensor_to_dict
from hydroserver.schemas import SensorInput
from sites.models import Sensor


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

    return JsonResponse(sensor_to_dict(sensor))


@api.get('/sensors', auth=jwt_auth)
def get_sensors(request):
    sensors = Sensor.objects.filter(Q(person=request.authenticated_user))
    return JsonResponse([sensor_to_dict(sensor) for sensor in sensors], safe=False)


@api.patch('/sensors/{sensor_id}', auth=jwt_auth)
def update_sensor(request, sensor_id: str, data: SensorInput):
    sensor = Sensor.objects.get(id=sensor_id)
    if request.authenticated_user != sensor.person:
        return JsonResponse({'detail': 'You are not authorized to update this sensor.'}, status=403)

    if data.name is not None:
        sensor.name = data.name
    if data.description is not None:
        sensor.description = data.description
    if data.manufacturer is not None:
        sensor.manufacturer = data.manufacturer
    if data.model is not None:
        sensor.model = data.model
    if data.method_type is not None:
        sensor.method_type = data.method_type
    if data.method_code is not None:
        sensor.method_code = data.method_code
    if data.method_link is not None:
        sensor.method_link = data.method_link
    if data.encoding_type is not None:
        sensor.encoding_type = data.encoding_type
    if data.model_url is not None:
        sensor.model_url = data.model_url

    sensor.save()

    return JsonResponse(sensor_to_dict(sensor))


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
