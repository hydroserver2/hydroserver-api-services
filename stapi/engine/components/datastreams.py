from uuid import UUID
from typing import List
from ninja.errors import HttpError
from core.endpoints.datastream.utils import query_datastreams
from sensorthings.components.datastreams.engine import DatastreamBaseEngine
from stapi.engine.utils import SensorThingsUtils


class DatastreamEngine(DatastreamBaseEngine, SensorThingsUtils):
    def get_datastreams(
            self,
            datastream_ids: List[UUID] = None,
            observed_property_ids: List[UUID] = None,
            sensor_ids: List[UUID] = None,
            thing_ids: List[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):

        datastreams, _ = query_datastreams(
            user=None,
            datastream_ids=datastream_ids
        )

        if filters:
            datastreams = self.apply_filters(
                queryset=datastreams,
                component='Datastream',
                filters=filters
            )

        count = datastreams.count()

        if pagination:
            datastreams = self.apply_pagination(
                queryset=datastreams,
                top=pagination.get('top'),
                skip=pagination.get('skip')
            )

        return [
            {
                'id': datastream.id,
                'name': str(datastream.name),
                'description': datastream.description,
                'thing_id': datastream.thing_id,
                'sensor_id': datastream.sensor_id,
                'observed_property_id': datastream.observed_property_id,
                'unit_of_measurement': {
                    'name': datastream.unit.name,
                    'symbol': datastream.unit.symbol,
                    'definition': datastream.unit.definition
                },
                'observation_type': datastream.observation_type,
                'observed_area': {},
                'phenomenon_time': None,
                'result_time': None,
                'properties': {
                    'result_type': datastream.result_type,
                    'status': datastream.status,
                    'sampled_medium': datastream.sampled_medium,
                    'value_count': datastream.value_count,
                    'no_data_value': datastream.no_data_value,
                    'processing_level_code': datastream.processing_level.code,
                    'intended_time_spacing': datastream.intended_time_spacing,
                    'intended_time_spacing_units': {
                        'name': datastream.intended_time_spacing_units.name,
                        'symbol': datastream.intended_time_spacing_units.symbol,
                        'definition': datastream.intended_time_spacing_units.definition
                    },
                    'aggregation_statistic': datastream.aggregation_statistic,
                    'time_aggregation_interval': datastream.time_aggregation_interval,
                    'time_aggregation_interval_units': {
                        'name': datastream.time_aggregation_interval_units.name,
                        'symbol': datastream.time_aggregation_interval_units.symbol,
                        'definition': datastream.time_aggregation_interval_units.definition
                    }
                }
            } for datastream in datastreams.all()
        ], count

    def create_datastream(
            self,
            datastream
    ) -> UUID:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_datastream(
            self,
            datastream_id: UUID,
            datastream
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_datastream(
            self,
            datastream_id: UUID
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
