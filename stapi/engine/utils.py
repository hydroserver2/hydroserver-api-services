from uuid import UUID
from django.db.models import F, Window, Prefetch
from django.db.models.functions import DenseRank
from django.core.exceptions import FieldError
from django.db.models.query import prefetch_related_objects
from ninja.errors import HttpError
from odata_query.django.django_q import AstToDjangoQVisitor
from sensorthings.components import field_schemas
from core import models as core_models


class SensorThingsUtils:
    @staticmethod
    def apply_pagination(queryset, top, skip):
        return queryset[skip: skip+top]

    @staticmethod
    def strings_to_uuids(strings):
        return [
            UUID(val) if isinstance(val, str) else val for val in strings
        ]

    def transform_model_field(self, component, prop):
        if component.__name__ == 'Thing':
            return {
                'properties__samplingFeatureType': 'sampling_feature_type',
                'properties__samplingFeatureCode': 'sampling_feature_code',
                'properties__siteType': 'site_type',
                'Location__id': 'location_id'
            }.get(prop, prop)

        elif component.__name__ == 'Location':
            return {
                'encodingType': 'location__encoding_type',
                'Thing__id': 'id'
            }.get(prop, f'location__{prop}')

        elif component.__name__ == 'HistoricalLocation':
            return prop

        elif component.__name__ == 'Sensor':
            return {
                'encodingType': 'encoding_type',
                'metadata__methodCode': 'method_code',
                'metadata__methodType': 'method_type',
                'metadata__methodLink': 'method_link',
                'metadata__sensorModel__sensorModelName': 'model',
                'metadata__sensorModel__sensorModelURL': 'model_link',
                'metadata__sensorModel__sensorManufacturer': 'manufacturer'
            }.get(prop, prop)

        elif component.__name__ == 'ObservedProperty':
            return {
                'properties__variableCode': 'code',
                'properties__variableType': 'type'
            }.get(prop, prop)

        elif component.__name__ == 'Datastream':
            if prop.split('__')[0] in [
                'Thing', 'Sensor', 'ObservedProperty'
            ]:
                return getattr(
                    field_schemas, prop.split('__')[0]
                ).Config.json_schema_extra['name_ref'][1] + '__' + self.transform_model_field(
                    component=getattr(field_schemas, prop.split('__')[0]),
                    prop='__'.join(prop.split('__')[1:])
                )
            else:
                return {
                    'unitOfMeasurement__name': 'unit__name',
                    'unitOfMeasurement__symbol': 'unit__symbol',
                    'unitOfMeasurement__definition': 'unit__definition',
                    'observationType': 'observation_type',
                    'observedArea': 'observed_area',
                    'properties__resultType': 'result_type',
                    'properties__status': 'status',
                    'properties__sampledMedium': 'sampled_medium',
                    'properties__valueCount': 'value_count',
                    'properties__noDataValue': 'no_data_value',
                    'properties__processingLevelCode': 'processing_level__code',
                    'properties__intendedTimeSpacing': 'intended_time_spacing',
                    'properties__intendedTimeSpacingUnitOfMeasurement': 'intended_time_spacing_units',
                    'properties__aggregationStatistic': 'aggregation_statistic',
                    'properties__timeAggregationInterval': 'time_aggregation_interval',
                    'properties__timeAggregationIntervalUnitOfMeasurement': 'time_aggregation_interval_units',
                }.get(prop, prop)

        elif component.__name__ == 'FeatureOfInterest':
            return prop

        elif component.__name__ == 'Observation':
            if prop.split('__')[0] in [
                'Datastream', 'FeatureOfInterest'
            ]:
                return getattr(
                    field_schemas, prop.split('__')[0]
                ).Config.json_schema_extra['name_ref'][1] + '__' + self.transform_model_field(
                    component=getattr(field_schemas, prop.split('__')[0]),
                    prop='__'.join(prop.split('__')[1:])
                )
            else:
                return {
                    'phenomenonTime': 'phenomenon_time',
                    'resultTime': 'result_time'
                }.get(prop, prop)

    def apply_filters(self, queryset, component, filters):
        """"""

        visitor = AstToDjangoQVisitor(getattr(core_models, component.__name__))
        query_filter = visitor.visit(filters)

        for prop in list(query_filter.flatten()):
            if isinstance(prop, F):
                model_field = self.transform_model_field(component, prop.name)
                prop.__dict__ = {
                    '_constructor_args': ((model_field,), {}),
                    'name': model_field
                }
        try:
            return queryset.filter(query_filter)
        except FieldError:
            raise HttpError(422, 'Failed to parse filter parameter.')

    def apply_order(self, queryset, component, order_by):
        """"""

        order_by = [
            {
                'field': self.transform_model_field(component, field['field'].replace('/', '__')),
                'direction': field['direction']
            } for field in order_by
        ]

        queryset = queryset.order_by(*[
            f'{"-" if order_field["direction"] == "desc" else ""}{order_field["field"]}'
            for order_field in order_by
        ])

        return queryset

    @staticmethod
    def apply_rank(component, queryset, partition_field, filter_ids, max_records=100):
        """"""

        total_query_limit = 100000  # TODO: Find a location in settings for this variable.

        ranked_queryset = queryset.filter(
            **{f'{partition_field}__in': filter_ids}
        ).annotate(
            rank=Window(
                expression=DenseRank(),
                partition_by=F(partition_field),
                order_by='pk'
            )
        )

        sql, params = ranked_queryset.query.sql_with_params()

        query = list(getattr(core_models, component.__name__).objects.raw("""
            SELECT * FROM ({}) ranked_result
            WHERE rank <= %s
            LIMIT %s
        """.format(sql), [*params, max_records, total_query_limit]))

        if hasattr(getattr(core_models, component.__name__), 'history'):
            prefetch_related_objects(
                query, Prefetch(
                    'log',
                    queryset=getattr(core_models, component.__name__).history.order_by('-history_date'), to_attr='ordered_log'
                )
            )

        return query
