from uuid import UUID
from typing import List
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
