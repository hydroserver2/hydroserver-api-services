from uuid import UUID
from ninja.errors import HttpError
from sensorthings.components.featuresofinterest.engine import FeatureOfInterestBaseEngine
from stapi.engine.utils import SensorThingsUtils


class FeatureOfInterestEngine(FeatureOfInterestBaseEngine, SensorThingsUtils):
    def get_features_of_interest(
            self,
            feature_of_interest_ids: list[UUID] = None,
            observation_ids: list[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (dict[str, dict], int):

        if get_count:
            count = 0
        else:
            count = None

        return {}, count

    def create_feature_of_interest(
            self,
            feature_of_interest
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_feature_of_interest(
            self,
            feature_of_interest_id: str,
            feature_of_interest
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_feature_of_interest(
            self,
            feature_of_interest_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
