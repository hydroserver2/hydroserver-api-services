from typing import List
from ninja.errors import HttpError
from django.db.models import Prefetch
from core.models import Thing
from sensorthings.components.locations.engine import LocationBaseEngine
from sensorthings.components.locations.schemas import Location as LocationSchema, LocationPostBody, LocationPatchBody
from stapi.engine.utils import SensorThingsUtils


class LocationEngine(LocationBaseEngine, SensorThingsUtils):
    def get_locations(
            self,
            location_ids: List[str] = None,
            thing_ids: List[str] = None,
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

        things = Thing.objects

        if thing_ids:
            things = things.filter(id__in=thing_ids)

        things = things.select_related('location').prefetch_associates().owner_is_active()

        if not expanded:
            things = things.owner(
                user=getattr(getattr(self, 'request', None), 'authenticated_user', None),
                include_public=True
            )

            if getattr(getattr(self, 'request', None), 'authenticated_user', None) and \
                    self.request.authenticated_user.permissions.enabled():  # noqa
                things = things.apply_permissions(
                    user=self.request.authenticated_user,  # noqa
                    method='GET'
                )

        things = things.prefetch_related(
            Prefetch('log', queryset=Thing.history.order_by('-history_date'), to_attr='ordered_log')
        )

        if filters:
            things = self.apply_filters(
                queryset=things,
                component=LocationSchema,
                filters=filters
            )

        if ordering:
            things = self.apply_order(
                queryset=things,
                component=LocationSchema,
                order_by=ordering
            )

        things = things.distinct()

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

        return {
            thing.location.id: {
                'id': thing.location.id,
                'name': thing.location.name,
                'description': thing.location.description,
                'encoding_type': thing.location.encoding_type,
                'location': {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            thing.location.latitude,
                            thing.location.longitude
                        ]
                    }
                },
                'properties': {
                    'elevation_m': thing.location.elevation_m,
                    'elevation_datum': thing.location.elevation_datum,
                    'state': thing.location.state,
                    'county': thing.location.county,
                    'last_updated': getattr(next(iter(thing.ordered_log), None), 'history_date', None)
                },
                'thing_ids': [thing.id]
            } for thing in things.all() if location_ids is None or thing.location.id in location_ids
        }, count

    def create_location(
            self,
            location: LocationPostBody
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_location(
            self,
            location_id: str,
            location: LocationPatchBody
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_location(
            self,
            location_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
