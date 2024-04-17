from typing import List
from ninja.errors import HttpError
from django.db.models import Prefetch
from sensorthings.components.sensors.engine import SensorBaseEngine
from core.models import Sensor
from stapi.engine.utils import SensorThingsUtils


class SensorEngine(SensorBaseEngine, SensorThingsUtils):
    def get_sensors(
            self,
            sensor_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (List[dict], int):

        if sensor_ids:
            sensor_ids = self.strings_to_uuids(sensor_ids)

        sensors = Sensor.objects

        if sensor_ids:
            sensors = sensors.filter(id__in=sensor_ids)

        sensors = sensors.prefetch_related(
            Prefetch('log', queryset=Sensor.history.order_by('-history_date'), to_attr='ordered_log')
        )

        if filters:
            sensors = self.apply_filters(
                queryset=sensors,
                component='Sensor',
                filters=filters
            )

        if ordering:
            sensors = self.apply_order(
                queryset=sensors,
                component='ObservedProperty',
                order_by=ordering
            )

        if get_count:
            count = sensors.count()
        else:
            count = None

        if pagination:
            sensors = self.apply_pagination(
                queryset=sensors,
                top=pagination.get('top'),
                skip=pagination.get('skip')
            )

        return [
            {
                'id': sensor.id,
                'name': sensor.name,
                'description': sensor.description,
                'encoding_type': sensor.encoding_type,
                'sensor_metadata': {
                    'method_code': sensor.method_code,
                    'method_type': sensor.method_type,
                    'method_link': sensor.method_link,
                    'sensor_model': {
                        'sensor_model_name': sensor.model,
                        'sensor_model_url': sensor.model_link,
                        'sensor_manufacturer': sensor.manufacturer
                    },
                    'last_updated': getattr(next(iter(sensor.ordered_log), None), 'history_date', None)
                },
                'properties': {}
            } for sensor in sensors.all() if sensor_ids is None or sensor.id in sensor_ids
        ], count

    def create_sensor(
            self,
            sensor
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_sensor(
            self,
            sensor_id: str,
            sensor
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_sensor(
            self,
            sensor_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
