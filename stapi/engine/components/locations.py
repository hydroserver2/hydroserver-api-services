from typing import List
from ninja.errors import HttpError
from core.endpoints.thing.utils import query_things
from sensorthings.components.locations.engine import LocationBaseEngine
from stapi.engine.utils import SensorThingsUtils


class LocationEngine(LocationBaseEngine, SensorThingsUtils):
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

        if filters:
            things = self.apply_filters(
                queryset=things,
                component='Location',
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
                    'county': thing.location.county
                },
                'thing_ids': [thing.id]
            } for thing in things.all() if location_ids is None or thing.location.id in location_ids
        ], count

    def create_location(
            self,
            location
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_location(
            self,
            location_id: str,
            location
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_location(
            self,
            location_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
