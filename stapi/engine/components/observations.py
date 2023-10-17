from uuid import UUID
from typing import List
from core.endpoints.observations.utils import query_observations
from core.endpoints.resultqualifier.utils import query_result_qualifiers, check_result_qualifier_by_id
from core.endpoints.datastream.utils import check_datastream_by_id
from core.models import Observation
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

        if filters:
            observations = self.apply_filters(
                queryset=observations,
                component='Observation',
                filters=filters
            )

        if not ordering:
            ordering = []

        if not all(field in [
            order_rule['field'] for order_rule in ordering
        ] for field in ['Datastream/id', 'phenomenonTime']):
            timestamp_direction = next(iter([
                order_rule['direction'] for order_rule in ordering
                if order_rule['field'] == 'phenomenonTime'
            ]), 'asc')
            ordering = [
                {'field': 'Datastream/id', 'direction': 'asc'},
                {'field': 'phenomenonTime', 'direction': timestamp_direction}
            ] + [
                order_rule for order_rule in ordering
                if order_rule['field'] not in ['Datastream/id', 'phenomenonTime']
            ]

        observations = self.apply_order(
            queryset=observations,
            component='Observation',
            order_by=ordering
        )

        count = observations.count()

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

        result_qualifier_ids = list(set([rq_id for rq_ids in [
            observation.result_qualifiers for observation in observations if observation.result_qualifiers
        ] for rq_id in rq_ids]))

        result_qualifiers, _ = query_result_qualifiers(
            user=None,
            result_qualifier_ids=result_qualifier_ids
        )

        result_qualifiers = {
            result_qualifier.id: result_qualifier
            for result_qualifier in result_qualifiers
        }

        return [
            {
                'id': observation.id,
                'phenomenon_time': str(observation.phenomenon_time),
                'result': observation.result,
                'result_time': str(observation.result_time) if observation.result_time else None,
                'datastream_id': observation.datastream_id,
                'result_quality': {
                    'quality_code': observation.quality_code,
                    'result_qualifiers': [
                        {
                            'code': result_qualifiers.get(result_qualifier).code,
                            'description': result_qualifiers.get(result_qualifier).description
                        } for result_qualifier in observation.result_qualifiers
                    ] if observation.result_qualifiers is not None else []
                }
            } for observation in observations
        ], count

    def create_observation(
            self,
            observation
    ) -> UUID:

        check_datastream_by_id(
            user=getattr(self, 'request').authenticated_user,
            datastream_id=observation.datastream.id,
            require_ownership=True,
            raise_http_errors=True
        )

        if observation.result_quality:
            for result_qualifier in observation.result_quality.result_qualifiers:
                check_result_qualifier_by_id(
                    user=getattr(self, 'request').authenticated_user,
                    result_qualifier_id=result_qualifier,
                    require_ownership=True,
                    raise_http_errors=True
                )

        new_observation = Observation.objects.create(
            datastream_id=observation.datastream.id,
            phenomenon_time=observation.phenomenon_time,
            result=observation.result,
            result_time=observation.result_time,
            quality_code=observation.result_quality.quality_code if observation.result_quality else None,
            result_qualifiers=observation.result_quality.result_qualifiers if observation.result_quality else []
        )

        return new_observation.id

    def create_observation_bulk(
            self,
            observations
    ) -> List[UUID]:

        new_observations = []

        for datastream_id, observation_array in observations.items():
            check_datastream_by_id(
                user=getattr(self, 'request').authenticated_user,
                datastream_id=datastream_id,
                require_ownership=True,
                raise_http_errors=True
            )

            for result_qualifier_id in list(set([result_qualifier for result_qualifiers in [
                observation.result_quality.result_qualifiers
                for observation in observation_array
                if observation.result_quality and observation.result_quality.result_qualifiers
            ] for result_qualifier in result_qualifiers])):
                check_result_qualifier_by_id(
                    user=getattr(self, 'request').authenticated_user,
                    result_qualifier_id=result_qualifier_id,
                    require_ownership=True,
                    raise_http_errors=True
                )

            new_observations_for_datastream = Observation.objects.bulk_create([
                Observation(
                    datastream_id=observation.datastream.id,
                    phenomenon_time=observation.phenomenon_time,
                    result=observation.result,
                    result_time=observation.result_time,
                    quality_code=observation.result_quality.quality_code if observation.result_quality else None,
                    result_qualifiers=observation.result_quality.result_qualifiers if observation.result_quality else []
                )
                for observation in observation_array
            ])

            new_observations.extend(new_observations_for_datastream)

        return [
            observation.id for observation in new_observations
        ]

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
