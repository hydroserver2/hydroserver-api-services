from uuid import UUID
from typing import List
from ninja.errors import HttpError
from sensorthings.components.featuresofinterest.engine import FeatureOfInterestBaseEngine
from sensorthings.components.featuresofinterest.schemas import FeatureOfInterestPostBody, FeatureOfInterestPatchBody
from stapi.engine.utils import SensorThingsUtils


class FeatureOfInterestEngine(FeatureOfInterestBaseEngine, SensorThingsUtils):
    def get_features_of_interest(
            self,
            feature_of_interest_ids: List[UUID] = None,
            observation_ids: List[UUID] = None,
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

    def create_feature_of_interest(
            self,
            feature_of_interest: FeatureOfInterestPostBody
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_feature_of_interest(
            self,
            feature_of_interest_id: str,
            feature_of_interest: FeatureOfInterestPatchBody
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_feature_of_interest(
            self,
            feature_of_interest_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
