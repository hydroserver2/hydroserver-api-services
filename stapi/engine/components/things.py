from uuid import UUID
from typing import List
from ninja.errors import HttpError
from core.endpoints.thing.utils import query_things
from sensorthings.components.things.engine import ThingBaseEngine
from stapi.engine.utils import SensorThingsUtils


class ThingEngine(ThingBaseEngine, SensorThingsUtils):
    def get_things(
            self,
            thing_ids: List[UUID] = None,
            location_ids: List[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):

        things, _ = query_things(
            user=None,
            thing_ids=thing_ids
        )

        if filters:
            things = self.apply_filters(
                queryset=things,
                component='Thing',
                filters=filters
            )

        count = things.count()

        if pagination:
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
                },
                'location_ids': [thing.location.id]
            } for thing in things.all() if location_ids is None or thing.location.id in location_ids
        ], count

    def create_thing(
            self,
            thing
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_thing(
            self,
            thing_id: str,
            thing
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_thing(
            self,
            thing_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
