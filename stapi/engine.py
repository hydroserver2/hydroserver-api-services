from typing import List
from uuid import UUID
from sensorthings import SensorThingsBaseEngine
from core.endpoints.thing.utils import query_things
from core.endpoints.datastream.utils import query_datastreams
from core.endpoints.sensor.utils import query_sensors


class HydroServerSensorThingsEngine(SensorThingsBaseEngine):

    def get_things(
            self,
            thing_ids: List[str] = None,
            location_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):

        things, _ = query_things(
            user=None,
            thing_ids=thing_ids
        )

        count = things.count()

        things = self.apply_pagination(
            queryset=things,
            top=pagination.get('top'),
            skip=pagination.get('skip')
        )

        return [
            {
                'id': thing.id,
                'name': thing.name,
                'description': thing.description,
                'properties': {
                    'sampling_feature_type': thing.sampling_feature_type,
                    'sampling_feature_code': thing.sampling_feature_code,
                    'site_type': thing.site_type,
                    'contact_people': []
                }
            } for thing in things.all() if location_ids is None or thing.location.id in location_ids
        ], count

    def create_thing(
            self,
            thing
    ) -> str:
        pass

    def update_thing(
            self,
            thing_id: str,
            thing
    ) -> None:
        pass

    def delete_thing(
            self,
            thing_id: str
    ) -> None:
        pass

    def get_locations(
            self,
            location_ids: List[str] = None,
            thing_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):

        things, _ = query_things(
            user=None,
            thing_ids=thing_ids
        )

        count = things.count()

        return [
            {
                'id': thing.location.id,
                'name': thing.location.name,
                'description': thing.location.description,
                'encoding_type': thing.location.encoding_type,
                'location': {
                    'latitude': thing.location.latitude,
                    'longitude': thing.location.longitude
                },
                'properties': {
                    'elevation_m': thing.location.elevation_m,
                    'elevation_datum': thing.location.elevation_datum,
                    'state': thing.location.state,
                    'county': thing.location.county
                }
            } for thing in things.all() if location_ids is None or thing.location.id in location_ids
        ], count

    def create_location(
            self,
            location
    ) -> str:
        pass

    def update_location(
            self,
            location_id: str,
            location
    ) -> None:
        pass

    def delete_location(
            self,
            location_id: str
    ) -> None:
        pass

    def get_historical_locations(
            self,
            historical_location_ids: List[str] = None,
            thing_ids: List[str] = None,
            location_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):
        return [], 0

    def create_historical_location(
            self,
            historical_location
    ) -> str:
        pass

    def update_historical_location(
            self,
            historical_location_id: str,
            historical_location
    ) -> None:
        pass

    def delete_historical_location(
            self,
            historical_location_id: str
    ) -> None:
        pass

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

        count = datastreams.count()

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
        pass

    def update_datastream(
            self,
            datastream_id: UUID,
            datastream
    ) -> None:
        pass

    def delete_datastream(
            self,
            datastream_id: UUID
    ) -> None:
        pass

    def get_sensors(
            self,
            sensor_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):

        sensors, _ = query_sensors(
            user=None,
            sensor_ids=sensor_ids
        )

        count = sensors.count()

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
                'metadata': {
                    'method_code': sensor.method_code,
                    'method_type': sensor.method_type,
                    'method_link': sensor.method_link,
                    'sensor_model': {
                        'sensor_model_name': sensor.model,
                        'sensor_model_url': sensor.model_link,
                        'sensor_manufacturer': sensor.manufacturer
                    }
                },
                'properties': {}
            } for sensor in sensors.all() if sensor_ids is None or sensor.id in sensor_ids
        ], count

    def create_sensor(
            self,
            sensor
    ) -> str:
        pass

    def update_sensor(
            self,
            sensor_id: str,
            sensor
    ) -> None:
        pass

    def delete_sensor(
            self,
            sensor_id: str
    ) -> None:
        pass

    def get_observed_properties(
            self,
            observed_property_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):
        return [], 0

    def create_observed_property(
            self,
            observed_property
    ) -> str:
        pass

    def update_observed_property(
            self,
            observed_property_id: str,
            observed_property
    ) -> None:
        pass

    def delete_observed_property(
            self,
            observed_property_id: str
    ) -> None:
        pass

    def get_observations(
            self,
            observation_ids: List[str] = None,
            datastream_ids: List[str] = None,
            feature_of_interest_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):
        return [], 0

    def create_observation(
            self,
            observation
    ) -> str:
        pass

    def update_observation(
            self,
            observation_id: str,
            observation
    ) -> None:
        pass

    def delete_observation(
            self,
            observation_id: str
    ) -> None:
        pass

    def get_features_of_interest(
            self,
            feature_of_interest_ids: List[str] = None,
            observation_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):
        return [], 0

    def create_feature_of_interest(
            self,
            feature_of_interest
    ) -> str:
        pass

    def update_feature_of_interest(
            self,
            feature_of_interest_id: str,
            feature_of_interest
    ) -> None:
        pass

    def delete_feature_of_interest(
            self,
            feature_of_interest_id: str
    ) -> None:
        pass

    @staticmethod
    def apply_pagination(queryset, top, skip):
        return queryset[skip: skip+top]
