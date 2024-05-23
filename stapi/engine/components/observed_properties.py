from uuid import UUID
from ninja.errors import HttpError
from django.db.models import Prefetch
from core.models import ObservedProperty
from sensorthings.components.observedproperties.engine import ObservedPropertyBaseEngine
from stapi.engine.utils import SensorThingsUtils


class ObservedPropertyEngine(ObservedPropertyBaseEngine, SensorThingsUtils):
    def get_observed_properties(
            self,
            observed_property_ids: list[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None,
            expanded: bool = False,
            get_count: bool = False
    ) -> (dict[str, dict], int):

        if observed_property_ids:
            observed_property_ids = self.strings_to_uuids(observed_property_ids)

        observed_properties = ObservedProperty.objects

        if observed_property_ids:
            observed_properties = observed_properties.filter(id__in=observed_property_ids)

        observed_properties = observed_properties.prefetch_related(
            Prefetch('log', queryset=ObservedProperty.history.order_by('-history_date'), to_attr='ordered_log')
        )

        if filters:
            observed_properties = self.apply_filters(
                queryset=observed_properties,
                component='ObservedProperty',
                filters=filters
            )

        if ordering:
            observed_properties = self.apply_order(
                queryset=observed_properties,
                component='ObservedProperty',
                order_by=ordering
            )

        if get_count:
            count = observed_properties.count()
        else:
            count = None

        if pagination:
            observed_properties = self.apply_pagination(
                queryset=observed_properties,
                top=pagination.get('top'),
                skip=pagination.get('skip')
            )

        return {
            observed_property.id: {
                'id': observed_property.id,
                'name': observed_property.name,
                'description': observed_property.description,
                'definition': observed_property.definition,
                'properties': {
                    'variable_code': observed_property.code,
                    'variable_type': observed_property.type,
                    'last_updated': getattr(next(iter(observed_property.ordered_log), None), 'history_date', None)
                }
            } for observed_property in observed_properties.all()
            if observed_property_ids is None or observed_property.id in observed_property_ids
        }, count

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
