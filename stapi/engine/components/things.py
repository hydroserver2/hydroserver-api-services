from uuid import UUID
from typing import List
from ninja.errors import HttpError
from django.db.models import Prefetch
from core.endpoints.thing.utils import query_things
from core.models import Thing
from sensorthings.components.things.engine import ThingBaseEngine
from stapi.engine.utils import SensorThingsUtils


class ThingEngine(ThingBaseEngine, SensorThingsUtils):
    def get_things(
            self,
            thing_ids: List[UUID] = None,
            location_ids: List[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (List[dict], int):

        if location_ids:
            location_ids = self.strings_to_uuids(location_ids)

        if thing_ids:
            thing_ids = self.strings_to_uuids(thing_ids)

        things, _ = query_things(
            user=getattr(getattr(self, 'request', None), 'authenticated_user', None),
            thing_ids=thing_ids,
            ignore_privacy=expanded
        )

        things = things.prefetch_related(
            Prefetch('log', queryset=Thing.history.order_by('-history_date'), to_attr='ordered_log')
        )

        if filters:
            things = self.apply_filters(
                queryset=things,
                component='Thing',
                filters=filters
            )

        if ordering:
            things = self.apply_order(
                queryset=things,
                component='Thing',
                order_by=ordering
            )

        if get_count:
            count = things.count()
        else:
            count = None

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
                    'contact_people': [
                        {
                            'first_name': thing_association.person.first_name,
                            'last_name': thing_association.person.last_name,
                            'email': thing_association.person.email,
                            'organization_name': getattr(thing_association.person.organization, 'name', None)
                        } for thing_association in thing.associates.all()
                    ],
                    'last_updated': getattr(next(iter(thing.ordered_log), None), 'history_date', None)
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
