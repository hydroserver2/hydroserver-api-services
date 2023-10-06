from uuid import UUID
from typing import List
from ninja.errors import HttpError
from core.endpoints.observedproperty.utils import query_observed_properties
from sensorthings.components.observedproperties.engine import ObservedPropertyBaseEngine
from stapi.engine.utils import SensorThingsUtils


class ObservedPropertyEngine(ObservedPropertyBaseEngine, SensorThingsUtils):
    def get_observed_properties(
            self,
            observed_property_ids: List[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> (List[dict], int):
        observed_properties, _ = query_observed_properties(
            user=None,
            observed_property_ids=observed_property_ids
        )

        if filters:
            observed_properties = self.apply_filters(
                queryset=observed_properties,
                component='ObservedProperty',
                filters=filters
            )

        count = observed_properties.count()

        if pagination:
            observed_properties = self.apply_pagination(
                queryset=observed_properties,
                top=pagination.get('top'),
                skip=pagination.get('skip')
            )

        return [
            {
                'id': observed_property.id,
                'name': observed_property.name,
                'description': observed_property.description,
                'definition': observed_property.definition,
                'properties': {
                    'variable_code': observed_property.code,
                    'variable_type': observed_property.type,
                }
            } for observed_property in observed_properties.all()
            if observed_property_ids is None or observed_property.id in observed_property_ids
        ], count

    def create_observed_property(
            self,
            observed_property
    ) -> str:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def update_observed_property(
            self,
            observed_property_id: str,
            observed_property
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')

    def delete_observed_property(
            self,
            observed_property_id: str
    ) -> None:
        raise HttpError(403, 'You do not have permission to perform this action.')
