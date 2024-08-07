from typing import List
from ninja.errors import HttpError
from sensorthings.components.historicallocations.engine import HistoricalLocationBaseEngine
from sensorthings.components.historicallocations.schemas import HistoricalLocationPostBody, HistoricalLocationPatchBody
from stapi.engine.utils import SensorThingsUtils


class HistoricalLocationEngine(HistoricalLocationBaseEngine, SensorThingsUtils):
    def get_historical_locations(
            self,
            historical_location_ids: List[str] = None,
            thing_ids: List[str] = None,
            location_ids: List[str] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (List[dict], int):

        if get_count:
            count = 0
        else:
            count = None

        return {}, count

    def create_historical_location(
            self,
            historical_location: HistoricalLocationPostBody
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_historical_location(
            self,
            historical_location_id: str,
            historical_location: HistoricalLocationPatchBody
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_historical_location(
            self,
            historical_location_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
