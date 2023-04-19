import uuid
import numpy as np
import pandas as pd
from typing import List, Union, Tuple, Optional
from odata_query.django.django_q import AstToDjangoQVisitor
from odata_query.rewrite import AliasRewriter
from django.core.exceptions import ObjectDoesNotExist
from django.urls.exceptions import Http404
from django.db.models.expressions import F
from hydrothings import SensorThingsAbstractEngine
from hydrothings.utils import lookup_component
from sensorthings.mapper import sensorthings_mapper
from sites import models as core_models


class SensorThingsEngine(SensorThingsAbstractEngine):
    rewriter = AliasRewriter({
        'Datastream': 'datastream',
    })

    def __init__(self, host: str, scheme: str, path: str, version: str, component: str):
        self.host = host
        self.scheme = scheme
        self.path = path
        self.component = component

    def get_fields(self, select=None):
        """"""

        if self.component == 'Observation':
            extra_fields = ['datastream_id']
        else:
            extra_fields = []

        if select is not None:
            select = [
                [field] for field in select.split(',')
            ]

        if not sensorthings_mapper.get(self.component):
            return []
        else:
            return [
                '__'.join(field) for field in sensorthings_mapper[self.component].get_output_paths(select)
            ] + extra_fields

    def resolve_entity_id_chain(self, entity_chain: List[Tuple[str, Union[uuid.UUID, int, str]]]) -> bool:
        """"""

        for i, entity in enumerate(entity_chain):
            if i == 0:
                if getattr(core_models, entity[0]).objects.filter(
                        pk=entity[1]
                ).exists() is False:
                    return False
            else:
                if getattr(core_models, entity[0]).filter(
                        **{
                            f'{lookup_component(entity_chain[i - 1][0], "camel_singular", "snake_singular")}_id':
                                entity_chain[i - 1][1]
                        }
                ).filter(
                    pk=entity[1]
                ).exists() is False:
                    return False

        return True

    def list(
            self,
            filters,
            count,
            order_by,
            skip,
            top,
            select,
            expand
    ) -> dict:
        """"""

        if self.component == 'Thing':
            query = core_models.ThingAssociation.objects
        elif hasattr(core_models, self.component):
            query = getattr(core_models, self.component).objects
        else:
            query = core_models.Thing.objects.none()

        response = {}

        if filters is not None:
            query = self.apply_filters(query, filters)

        response_count = self.get_count(query)

        if order_by is not None:
            query = self.apply_order(query, order_by)

        # if expand is not None:
        #     query = self.apply_expand(query, expand)

        if count is True:
            response['count'] = response_count

        if top is None:
            if self.component == 'Observation':
                top = 1000
            else:
                top = 100

        if skip is None:
            skip = 0

        queryset = query.values(*self.get_fields(select))
        queryset = self.apply_pagination(queryset, top, skip)

        response_df = pd.DataFrame(list(queryset))
        response_df = self.transform_response(response_df)

        response_value = response_df.to_dict('records')

        response_value = [
            self.build_related_links(entity, is_collection=True)
            for entity in response_value
        ]
        response_value = [
            self.build_self_links(entity, is_collection=True)
            for entity in response_value
        ]

        response['value'] = response_value
        response['next_link'] = self.build_next_link(top, skip)

        return response

    def get(
            self,
            entity_id
    ) -> Optional[dict]:
        """"""

        if self.component == 'Thing':
            query = core_models.ThingAssociation.objects
            query = query.filter(thing__id=entity_id)
        elif self.component in ['FeatureOfInterest', 'HistoricalLocation']:
            return None
        else:
            query = getattr(core_models, self.component).objects
            query = query.filter(pk=entity_id)

        queryset = query.values(*self.get_fields())

        response_df = pd.DataFrame(list(queryset))
        response_df = self.transform_response(response_df)

        try:
            response = response_df.to_dict('records')[0]
        except IndexError:
            return None

        response = self.build_related_links(response)
        response = self.build_self_links(response)

        return response

    def create(
            self,
            entity_body
    ) -> str:
        """"""

        return '0'

    def bulk_create(
            self,
            entity_bodies
    ) -> List[str]:

        if self.component == 'Observation':
            entities = getattr(core_models, self.component).objects.bulk_create(
                [
                    getattr(core_models, self.component)(
                        id=uuid.uuid4(),
                        datastream_id=entity_body.datastream.id,
                        result=entity_body.result,
                        result_time=entity_body.result_time,
                        result_quality=entity_body.result_quality,
                        phenomenon_time=entity_body.phenomenon_time,
                        valid_begin_time=entity_body.valid_time,
                        valid_end_time=entity_body.valid_time,
                    ) for entity_body in entity_bodies
                ]
            )

        else:
            entities = []

        return [entity.id for entity in entities]

    def update(
            self,
            entity_id,
            entity_body
    ) -> str:
        """"""

        try:
            entity = getattr(core_models, self.component).objects.get(pk=entity_id)
        except ObjectDoesNotExist:
            raise Http404

        # entity_fields = self.transform_body(entity_body)
        #
        # for attr, value in entity_fields.items():
        #     setattr(entity, attr, value)
        #
        # entity.save()

        return entity_id

    def delete(
            self,
            entity_id
    ) -> None:
        """"""

        return None

    def get_count(self, query):
        """
        Returns a count of the objects that would be returned by the given query.

        :param query: The query object to be counted.
        :return count: A count of the objects in the resulting queryset.
        """

        if self.component == 'Thing':
            return query.values('thing__id').distinct().count()
        else:
            return query.count()

    @staticmethod
    def format_isointerval(start_time, end_time):
        """"""

        if pd.isnull(start_time) and pd.isnull(end_time):
            return None
        elif pd.isnull(start_time):
            return end_time.strftime('%Y-%m-%d %H:%M:%S') + '/' + end_time.strftime('%Y-%m-%d %H:%M:%S')
        elif pd.isnull(end_time):
            return start_time.strftime('%Y-%m-%d %H:%M:%S') + '/' + start_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return start_time.strftime('%Y-%m-%d %H:%M:%S') + '/' + end_time.strftime('%Y-%m-%d %H:%M:%S')


    def transform_response(self, response_df):
        """"""

        response_df = response_df.replace({np.nan: None})

        if response_df.empty:
            pass
        elif self.component == 'Thing':
            response_df = response_df.rename(columns={
                'thing__id': 'id', 'thing__name': 'name', 'thing__description': 'description',
                'person__first_name': 'first_name', 'person__last_name': 'last_name', 'person__email': 'email',
                'person__organization': 'organization', 'person__phone': 'phone'
            })
            response_df = response_df.groupby([
                'id', 'name', 'description', 'thing__sampling_feature_code', 'thing__sampling_feature_type',
                'thing__site_type'
            ]).apply(
                lambda row: row[
                    ['first_name', 'last_name', 'email', 'organization', 'phone']
                ].to_dict('records')
            ).reset_index(name='contacts')
            response_df['properties'] = response_df.apply(
                lambda row: {
                    'sampling_feature_code': row['thing__sampling_feature_code'],
                    'sampling_feature_type': row['thing__sampling_feature_type'],
                    'site_type': row['thing__site_type'],
                    'contact_people': row['contacts']
                }, axis=1
            )
        elif self.component == 'Location':
            response_df = response_df.rename(columns={
                'thing_id': 'id'
            })
            response_df['location'] = response_df.apply(
                lambda row: {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            row['latitude'],
                            row['longitude']
                        ]
                    },
                    'properties': {
                        'city': row['city']
                    }
                }, axis=1
            )
            response_df['properties'] = response_df.apply(
                lambda row: {
                    'city': row['city'],
                    'state': row['state'],
                    'county': row['country'],
                    'elevation': row['elevation'],
                    'elevation_datum': row['elevation_datum']
                }, axis=1
            )
        elif self.component == 'ObservedProperty':
            response_df['properties'] = response_df.apply(
                lambda row: {
                    'variable_code': row['variable_code'],
                    'variable_type': row['variable_type']
                }, axis=1
            )
        elif self.component == 'Sensor':
            response_df['sensor_metadata'] = response_df.apply(
                lambda row: {
                    'method_code': row['method_code'],
                    'method_type': row['method_type'],
                    'method_link': row['method_link'],
                    'sensor_model': {
                        'sensor_model_name': row['model'],
                        'sensor_manufacturer': row['manufacturer'],
                        'sensor_model_url': row['model_url']
                    }
                }, axis=1
            )
        elif self.component == 'Datastream':
            response_df['unit_of_measurement'] = response_df.apply(
                lambda row: {
                    'name': row['unit__name'],
                    'symbol': row['unit__symbol'],
                    'definition': row['unit__definition']
                }, axis=1
            )
            response_df['properties'] = response_df.apply(
                lambda row: {
                    'result_type': row['result_type'],
                    'status': row['status'],
                    'sampled_medium': row['sampled_medium'],
                    'value_count': row['value_count'] if not pd.isnull(row['value_count']) else 0,
                    'no_data_value': row['no_data_value'],
                    'processing_level_code': row['processing_level__processing_level_code'],
                    'intended_time_spacing': row['intended_time_spacing'],
                    'intended_time_spacing_unit_of_measurement': {
                        'name': row['intended_time_spacing_units__name'],
                        'symbol': row['intended_time_spacing_units__symbol'],
                        'definition': row['intended_time_spacing_units__definition']
                    },
                    'aggregation_statistic': row['aggregation_statistic'],
                    'time_aggregation_interval': row['time_aggregation_interval'],
                    'time_aggregation_interval_unit_of_measurement': {
                        'name': row['time_aggregation_interval_units__name'],
                        'symbol': row['time_aggregation_interval_units__symbol'],
                        'definition': row['time_aggregation_interval_units__definition']
                    },
                    'phenomenon_time': self.format_isointerval(
                        row['phenomenon_start_time'], row['phenomenon_end_time']
                    ),
                    'result_time': self.format_isointerval(
                        row['result_begin_time'], row['result_end_time']
                    )
                }, axis=1
            )
        elif self.component == 'Observation':
            response_df['result_time'] = response_df.apply(
                lambda row: row['result_time'].strftime('%Y-%m-%d %H:%M:%S'),
                axis=1
            )

        return response_df

    def transform_body(self, entity_body):
        """"""

        if self.component == 'Thing':
            entity_fields = {
                'id': uuid.uuid4(),
                'name': entity_body.name,
                'description': entity_body.description,
                'sampling_feature_code': entity_body.properties.get('sampling_feature_code'),
                'sampling_feature_type': entity_body.properties.get('sampling_feature_type'),
                'site_type': entity_body.properties.get('site_type')
            }
        elif self.component == 'Location':
            entity_fields = {

            }
        elif self.component == 'ObservedProperty':
            entity_fields = {

            }
        elif self.component == 'Sensor':
            entity_fields = {

            }
        elif self.component == 'Datastream':
            entity_fields = {

            }
        elif self.component == 'Observation':
            entity_fields = {

            }
        else:
            entity_fields = {}

        return {}

    def apply_order(self, query, order_by):
        """"""

        order_map = {
            'Datastreams/id': 'datastream_id'
        }

        query = query.order_by(*[
            f"{'-' if order_field['direction'] == 'desc' else ''}{order_map.get(order_field['field'], order_field['field'])}"
            for order_field in order_by
        ])

        return query

    def apply_filters(self, query, filters):
        """"""

        filters = self.rewriter.visit(filters)
        visitor = AstToDjangoQVisitor(getattr(core_models, self.component))
        query_filter = visitor.visit(filters)

        field_map = sensorthings_mapper[self.component].get_output_field_map(
            input_delimiter='__',
            output_delimiter='__'
        )

        for prop in list(query_filter.flatten()):
            if isinstance(prop, F) and prop.name in field_map.keys():
                prop.__dict__ = {
                    '_constructor_args': ((field_map[prop.name],), {}),
                    'name': field_map[prop.name]
                }

        query = query.filter(query_filter)

        return query

    def apply_pagination(self, queryset, top, skip):
        """"""

        queryset = queryset[skip: skip+top]

        return queryset
