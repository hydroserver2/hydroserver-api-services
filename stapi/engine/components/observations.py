import math
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from django.db.utils import IntegrityError
from ninja.errors import HttpError
from core.models import Observation, ResultQualifier, Datastream
from sensorthings.components.observations.engine import ObservationBaseEngine
from sensorthings.components.observations.schemas import Observation as ObservationSchema, ObservationPatchBody
from stapi.schemas.observations import ObservationPostBody
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
            expanded: bool = False,
            get_count: bool = False
    ) -> (List[dict], int):

        if observation_ids:
            observation_ids = self.strings_to_uuids(observation_ids)

        observations = Observation.objects

        if observation_ids:
            observations = observations.filter(id__in=observation_ids)

        observations = observations.owner_is_active()

        if not expanded:
            observations = observations.owner(
                user=getattr(getattr(self, 'request', None), 'authenticated_user', None),
                include_public=True
            )

            if getattr(getattr(self, 'request', None), 'authenticated_user', None) and \
                    self.request.authenticated_user.permissions.enabled():  # noqa
                observations = observations.apply_permissions(
                    user=self.request.authenticated_user,  # noqa
                    method='GET'
                )

        if filters:
            observations = self.apply_filters(
                queryset=observations,
                component=ObservationSchema,
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
            component=ObservationSchema,
            order_by=ordering
        )

        observations = observations.distinct()

        if get_count:
            count = observations.count()
        else:
            count = None

        if datastream_ids:
            observations = self.apply_rank(
                component=ObservationSchema,
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

        result_qualifiers = ResultQualifier.objects.filter(id__in=result_qualifier_ids)

        result_qualifiers = {
            result_qualifier.id: result_qualifier
            for result_qualifier in result_qualifiers
        }

        return {
            observation.id: {
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
        }, count

    def create_observation(
            self,
            observation: ObservationPostBody
    ) -> UUID:

        datastream = Datastream.objects.get_by_id(
            datastream_id=observation.datastream.id,
            user=getattr(self, 'request').authenticated_user,
            method='POST',
            model='Observation',
            raise_404=True
        )

        if observation.result_quality:
            for result_qualifier in observation.result_quality.result_qualifiers:
                ResultQualifier.objects.get_by_id(
                    result_qualifier_id=result_qualifier,
                    user=getattr(self, 'request').authenticated_user,
                    method='GET',
                    fetch=False,
                    raise_404=True
                )

        try:
            new_observation = Observation.objects.create(
                datastream_id=observation.datastream.id,
                phenomenon_time=observation.phenomenon_time,
                result=observation.result if not math.isnan(observation.result) else datastream.no_data_value,
                result_time=observation.result_time,
                quality_code=observation.result_quality.quality_code if observation.result_quality else None,
                result_qualifiers=observation.result_quality.result_qualifiers if observation.result_quality else []
            )
        except IntegrityError:
            raise HttpError(409, 'Duplicate phenomenonTime found on this datastream.')

        self.update_value_count(datastream_id=observation.datastream.id)

        return new_observation.id

    def create_observations(
            self,
            observations
    ) -> List[UUID]:

        new_observations = []

        for datastream_id, datastream_observations in observations.items():
            datastream = Datastream.objects.get_by_id(
                datastream_id=datastream_id,
                user=getattr(self, 'request').authenticated_user,
                method='POST',
                model='Observation',
                raise_404=True
            )

            for result_qualifier_id in list(set([result_qualifier for result_qualifiers in [
                observation.result_quality.result_qualifiers
                for observation in datastream_observations
                if observation.result_quality and observation.result_quality.result_qualifiers
            ] for result_qualifier in result_qualifiers])):
                ResultQualifier.objects.get_by_id(
                    result_qualifier_id=result_qualifier_id,
                    user=getattr(self, 'request').authenticated_user,
                    method='GET',
                    fetch=False,
                    raise_404=True
                )

            try:
                new_observations_for_datastream = Observation.objects.bulk_create([
                    Observation(
                        datastream_id=observation.datastream.id,
                        phenomenon_time=observation.phenomenon_time,
                        result=observation.result if not math.isnan(observation.result) else datastream.no_data_value,
                        result_time=observation.result_time,
                        quality_code=observation.result_quality.quality_code if observation.result_quality else None,
                        result_qualifiers=observation.result_quality.result_qualifiers
                        if observation.result_quality else []
                    )
                    for observation in datastream_observations
                ])
            except IntegrityError:
                raise HttpError(409, 'Duplicate phenomenonTime found on this datastream.')

            new_observations.extend(new_observations_for_datastream)

            self.update_value_count(datastream_id=datastream_id)

        return [
            observation.id for observation in new_observations
        ]

    def update_observation(
            self,
            observation_id: str,
            observation: ObservationPatchBody
    ) -> None:
        pass

    def delete_observation(
            self,
            observation_id: str
    ) -> None:
        pass

    def delete_observations(
            self,
            datastream_id: UUID,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None
    ) -> None:
        return None

    def update_value_count(
            self,
            datastream_id: UUID
    ) -> None:

        observation_query = Observation.objects.filter(
            datastream_id=datastream_id
        ).owner(user=getattr(getattr(self, 'request', None), 'authenticated_user', None))

        datastream = Datastream.objects.get_by_id(
            datastream_id=datastream_id,
            user=getattr(getattr(self, 'request', None), 'authenticated_user', None),
            method='PATCH',
            model='Datastream',
            raise_404=True
        )

        datastream.value_count = int(observation_query.count())
        datastream.save()
