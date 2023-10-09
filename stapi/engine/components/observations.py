from uuid import UUID
from typing import List
from core.endpoints.observations.utils import query_observations
from sensorthings.components.observations.engine import ObservationBaseEngine
from stapi.engine.utils import SensorThingsUtils


class ObservationEngine(ObservationBaseEngine, SensorThingsUtils):
    def get_observations(
            self,
            observation_ids: List[UUID] = None,
            datastream_ids: List[UUID] = None,
            feature_of_interest_ids: List[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False
    ) -> (List[dict], int):

        if observation_ids:
            observation_ids = self.strings_to_uuids(observation_ids)

        observations, _ = query_observations(
            user=getattr(getattr(self, 'request', None), 'authenticated_user', None),
            observation_ids=observation_ids,
            ignore_privacy=expanded
        )

        count = observations.count()

        if filters:
            observations = self.apply_filters(
                queryset=observations,
                component='Observation',
                filters=filters
            )

        if datastream_ids:
            observations = self.apply_rank(
                component='Observation',
                queryset=observations,
                partition_field='datastream_id',
                filter_ids=datastream_ids,
                max_records=1000
            )
        else:
            if pagination:
                observations = self.apply_pagination(
                    queryset=observations,
                    top=pagination.get('top'),
                    skip=pagination.get('skip')
                )
            observations = observations.all()

        result_qualifiers = {}

        return [
            {
                'id': observation.id,
                'phenomenon_time': observation.phenomenon_time,
                'result': observation.result,
                'result_time': observation.result_time,
                'result_quality': {
                    'quality_code': observation.quality_code,
                    'result_qualifiers': [
                        {
                            'code': result_qualifiers.get(result_qualifier)['code'],
                            'description': result_qualifiers.get(result_qualifier)['description']
                        } for result_qualifier in observation.result_qualifiers
                    ]
                }
            } for observation in observations
        ], count

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
