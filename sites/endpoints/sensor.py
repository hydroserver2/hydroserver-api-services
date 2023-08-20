from django.db.models import Q
from django.http import JsonResponse
from ninja import Router, Schema

from sites.models import Sensor
from sites.utils.authentication import jwt_auth
from sites.utils.sensor import sensor_to_dict

router = Router()


class SensorInput(Schema):
    name: str = None
    description: str = None
    encoding_type: str = None
    manufacturer: str = None
    model: str = None
    model_url: str = None
    method_type: str = None
    method_link: str = None
    method_code: str = None


@router.post('', auth=jwt_auth)
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
        encoding_type="application/json",
        model_url=data.model_url,
    )

    return JsonResponse(sensor_to_dict(sensor))


@router.get('', auth=jwt_auth)
def get_sensors(request):
    sensors = Sensor.objects.filter(Q(person=request.authenticated_user))
    return JsonResponse([sensor_to_dict(sensor) for sensor in sensors], safe=False)


@router.patch('/{sensor_id}', auth=jwt_auth)
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
    # Should always be JSON
    # if data.encoding_type is not None:
    #     sensor.encoding_type = data.encoding_type
    if data.model_url is not None:
        sensor.model_url = data.model_url

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
