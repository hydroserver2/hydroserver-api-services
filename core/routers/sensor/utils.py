from django.db.models import Q
from core.models import Sensor
from .schemas import SensorFields


def query_sensors(user=None, sensor_ids=None):
    """"""

    sensor_query = Sensor.objects.filter(Q(person=user))

    if sensor_ids:
        sensor_query = sensor_query.filter(
            id__in=sensor_ids
        )

    sensors = [
        {
            'id': sensor.id,
            **{field: getattr(sensor, field) for field in SensorFields.__fields__.keys()},
        } for sensor in sensor_query.all()
    ]

    return sensors


def get_sensor_by_id(user, sensor_id):
    """"""

    return next(iter(query_sensors(
        user=user,
        sensor_ids=[sensor_id]
    )), None)
