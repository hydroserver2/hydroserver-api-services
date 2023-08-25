import uuid
import numpy as np
import pandas as pd
from typing import List, Union, Tuple, Optional
from pydantic.fields import SHAPE_LIST
from odata_query.django.django_q import AstToDjangoQVisitor
from odata_query.rewrite import AliasRewriter
from django.core.exceptions import ObjectDoesNotExist
from django.urls.exceptions import Http404
from django.db import connection
from django.db.models import F, Window
from django.db.models.functions import DenseRank
from sensorthings import SensorThingsAbstractEngine
from sensorthings import components as component_schemas
from sensorthings.utils import lookup_component
from stapi.mapper import sensorthings_mapper
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
        self.version = version

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

    def get_fields(self, query_structure, prefix='', df_prefixes=None):
        """"""

        component = query_structure['component']
        prefetch_components = sensorthings_mapper[component].get_output_components(
            query_structure.get('select'),
            prefix=prefix,
            delimiter='__'
        )
        if df_prefixes is None:
            df_prefixes = []

        related_fields = [
            prefix + '__'.join(field) for field in sensorthings_mapper[component].get_output_paths(
                query_structure.get('select')
            )
        ]

        for child_structure in query_structure.get('children', []):
            if child_structure['array'] is False:
                new_prefix = prefix + lookup_component(
                    child_structure['component'],
                    'camel_singular',
                    'snake_singular'
                ) + '__'
                child_related_fields, related_prefetch_components, df_prefixes = self.get_fields(
                    query_structure=child_structure,
                    prefix=new_prefix,
                    df_prefixes=df_prefixes
                )
                df_prefixes.append({
                    'component': child_structure['component'],
                    'prefix': new_prefix
                })
                related_fields.extend(child_related_fields)
                prefetch_components.extend(related_prefetch_components)
            else:
                if component == 'Location':
                    prefetch_field = 'id'
                else:
                    prefetch_field = lookup_component(component, 'camel_singular', 'snake_singular') + '_id'

                prefetch_components.append({
                    'component': child_structure['component'],
                    'prefetch_filter': f'{prefix}id',
                    'query_structure': child_structure,
                    'prefetch_field': prefetch_field
                })

        extra_fields = [prefix + 'datastream_id'] if component == 'Observation' else []

        return related_fields + extra_fields, prefetch_components, df_prefixes

    def build_querysets(self, query_structure, prefetch_field=None, prefetch_filter=None):
        """"""

        component = query_structure['component']
        queryset = getattr(core_models, component).objects

        related_fields, prefetch_components, df_prefixes = self.get_fields(query_structure)

        aliased_fields = {
            f'a_{related_field}': F(related_field)
            for related_field in related_fields
        }

        if component == 'Location':
            aliased_fields['a_id'] = F('thing_id')

        if component == 'Thing':
            aliased_fields['a_location_id'] = F('id')

        queryset = queryset.values(**aliased_fields)

        if query_structure.get('order_by'):
            queryset = self.apply_order(queryset, query_structure['order_by'])

        if query_structure.get('pk'):
            queryset = queryset.filter(pk=query_structure['pk'])

        if query_structure.get('filters'):
            queryset = self.apply_filters(queryset, query_structure['filters'])

        if query_structure.get('count') is True:
            queryset_count = queryset.count()
        else:
            queryset_count = None

        if query_structure.get('pagination'):
            queryset = self.apply_pagination(
                queryset,
                query_structure['pagination']['top'],
                query_structure['pagination']['skip']
            )

        prefetch_querysets = [
            self.build_querysets(
                query_structure=prefetch_component['query_structure'],
                prefetch_field=prefetch_component['prefetch_field'],
                prefetch_filter=prefetch_component['prefetch_filter'],
            ) for prefetch_component in prefetch_components
        ]

        df_prefixes.append({
            'component': component,
            'prefix': ''
        })

        return {
            'component': component,
            'queryset': queryset,
            'count': queryset_count,
            'prefetch_field': prefetch_field,
            'prefetch_filter': prefetch_filter,
            'prefetch': prefetch_querysets,
            'df_prefixes': df_prefixes
        }

    @staticmethod
    def raw_query_to_dicts(query_string, *query_args):
        cursor = connection.cursor()
        cursor.execute(query_string, query_args)
        col_names = [desc[0] for desc in cursor.description]
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            row_dict = dict(zip(col_names, row))
            yield row_dict
        return

    def fetch_data(self, querysets):

        query = querysets['queryset']

        if querysets.get('prefetch_field'):
            query = query.annotate(
                rank=Window(
                    expression=DenseRank(),
                    partition_by=F(querysets['prefetch_field']),
                    order_by='pk'
                )
            )
            sql, params = query.query.sql_with_params()
            params = [f"'{param}'" if isinstance(param, uuid.UUID) else param for param in params]
            rank_group_limit = 1000
            total_query_limit = 10000

            query = getattr(core_models, querysets['component']).objects.raw("""
                SELECT * FROM ({}) ranked_result
                WHERE rank <= %s
                LIMIT %s
            """.format(sql), [*params, rank_group_limit, total_query_limit])

            df = pd.DataFrame(list(self.raw_query_to_dicts(str(query.query))))

        else:
            df = pd.DataFrame(list(query))

        child_dfs = []

        if not df.empty:
            df.replace({np.nan: None}, inplace=True)
            df.rename(columns=lambda x: x[2:], inplace=True)

            for prefetch in querysets['prefetch']:
                print(df)
                prefetch['queryset'] = prefetch['queryset'].filter(
                    **{f"{prefetch['prefetch_field']}__in": df[prefetch['prefetch_filter']].tolist()}
                )
                child_dfs.append(self.fetch_data(prefetch))

        return {
            'df': df,
            'component': querysets['component'],
            'prefetch_prefix': querysets['prefetch_filter'][:-2] if querysets['prefetch_filter'] else '',
            'df_prefixes': querysets['df_prefixes'],
            'child_dfs': child_dfs
        }

    def transform_dataframes(self, dataframes):
        """"""

        df = dataframes['df']

        for df_prefix in dataframes['df_prefixes']:
            for child_df in [
                child_df for child_df in dataframes['child_dfs']
                if child_df['prefetch_prefix'] == df_prefix['prefix']
            ]:
                transformed_child_df = self.transform_dataframes(child_df)

                if child_df['component'] == 'ThingAssociation':
                    merged_field_name = 'thing_associations'
                else:
                    merged_field_name = lookup_component(
                        child_df['component'], 'camel_singular', 'snake_plural'
                    ) + '_rel'

                if child_df['component'] == 'Location':
                    child_merge_group_column = 'id'
                else:
                    child_merge_group_column = (
                        lookup_component(df_prefix['component'], 'camel_singular', 'snake_singular') + '_id'
                    )

                df = self.merge_dataframes(
                    parent_df=df,
                    child_df=transformed_child_df,
                    merged_field_name=merged_field_name,
                    parent_merge_join_column='id',
                    parent_merge_join_prefix=df_prefix['prefix'],
                    child_merge_group_column=child_merge_group_column
                )

            df = self.apply_transformations(
                df,
                df_prefix['component'],
                df_prefix['prefix'],
                dataframes['component'] if df_prefix['component'] != dataframes['component'] else None
            )

        return df

    @staticmethod
    def merge_dataframes(
            parent_df,
            child_df,
            merged_field_name,
            parent_merge_join_column,
            parent_merge_join_prefix,
            child_merge_group_column
    ):
        """"""

        child_df = child_df.groupby([child_merge_group_column]).apply(
            lambda row: row[
                [col for col in child_df.columns if col != child_merge_group_column]
            ].to_dict('records')
        ).reset_index(name=f'{parent_merge_join_prefix}{merged_field_name}')

        parent_df = parent_df.merge(
            child_df,
            left_on=parent_merge_join_prefix + parent_merge_join_column,
            right_on=child_merge_group_column,
            suffixes=['', '_x']
        )

        return parent_df

    def apply_transformations(self, df, component, prefix, parent_component=None):
        """"""

        if df.empty:
            return df

        if component == 'ThingAssociation':
            df.rename(columns={
                'person__email': 'email', 'person__first_name': 'first_name', 'person__last_name': 'last_name',
                'person__phone': 'phone'
            }, inplace=True)
        if component == 'Thing':
            df[f'{prefix}properties'] = df.apply(
                lambda row: {
                    'sampling_feature_code': row[f'{prefix}sampling_feature_code'],
                    'sampling_feature_type': row[f'{prefix}sampling_feature_type'],
                    'site_type': row[f'{prefix}site_type'],
                    'contact_people': row[f'{prefix}thing_associations']
                }, axis=1
            )
        elif component == 'Location':
            if f'{prefix}id' not in df:
                df.rename(columns={
                    f'{prefix}thing_id': f'{prefix}id'
                }, inplace=True)
            df[f'{prefix}location'] = df.apply(
                lambda row: {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            row[f'{prefix}latitude'],
                            row[f'{prefix}longitude']
                        ]
                    },
                    'properties': {
                        'city': row[f'{prefix}city']
                    }
                }, axis=1
            )
            df[f'{prefix}properties'] = df.apply(
                lambda row: {
                    'city': row[f'{prefix}city'],
                    'state': row[f'{prefix}state'],
                    'county': row[f'{prefix}county'],
                    'elevation': row[f'{prefix}elevation'],
                    'elevation_datum': row[f'{prefix}elevation_datum']
                }, axis=1
            )
        elif component == 'ObservedProperty':
            df[f'{prefix}properties'] = df.apply(
                lambda row: {
                    'variable_code': row[f'{prefix}variable_code'],
                    'variable_type': row[f'{prefix}variable_type']
                }, axis=1
            )
        elif component == 'Sensor':
            df[f'{prefix}sensor_metadata'] = df.apply(
                lambda row: {
                    'method_code': row[f'{prefix}method_code'],
                    'method_type': row[f'{prefix}method_type'],
                    'method_link': row[f'{prefix}method_link'],
                    'sensor_model': {
                        'sensor_model_name': row[f'{prefix}model'],
                        'sensor_manufacturer': row[f'{prefix}manufacturer'],
                        'sensor_model_url': row[f'{prefix}model_url']
                    }
                }, axis=1
            )
        elif component == 'Datastream':
            df[f'{prefix}unit_of_measurement'] = df.apply(
                lambda row: {
                    'name': row[f'{prefix}unit__name'],
                    'symbol': row[f'{prefix}unit__symbol'],
                    'definition': row[f'{prefix}unit__definition']
                }, axis=1
            )
            df[f'{prefix}phenomenon_time'] = df.apply(
                lambda row: self.format_isointerval(
                    row[f'{prefix}phenomenon_start_time'], row[f'{prefix}phenomenon_end_time']
                ), axis=1
            )
            df[f'{prefix}result_time'] = df.apply(
                lambda row: self.format_isointerval(
                    row[f'{prefix}result_begin_time'], row[f'{prefix}result_end_time']
                ), axis=1
            )
            df[f'{prefix}properties'] = df.apply(
                lambda row: {
                    'result_type': row[f'{prefix}result_type'],
                    'status': row[f'{prefix}status'],
                    'sampled_medium': row[f'{prefix}sampled_medium'],
                    'value_count': row[f'{prefix}value_count'] if not pd.isnull(row[f'{prefix}value_count']) else 0,
                    'no_data_value': row[f'{prefix}no_data_value'],
                    'processing_level_code': row[f'{prefix}processing_level__processing_level_code'],
                    'intended_time_spacing': row[f'{prefix}intended_time_spacing'],
                    'intended_time_spacing_unit_of_measurement': {
                        'name': row[f'{prefix}intended_time_spacing_units__name'],
                        'symbol': row[f'{prefix}intended_time_spacing_units__symbol'],
                        'definition': row[f'{prefix}intended_time_spacing_units__definition']
                    },
                    'aggregation_statistic': row[f'{prefix}aggregation_statistic'],
                    'time_aggregation_interval': row[f'{prefix}time_aggregation_interval'],
                    'time_aggregation_interval_unit_of_measurement': {
                        'name': row[f'{prefix}time_aggregation_interval_units__name'],
                        'symbol': row[f'{prefix}time_aggregation_interval_units__symbol'],
                        'definition': row[f'{prefix}time_aggregation_interval_units__definition']
                    }
                }, axis=1
            )
        elif component == 'Observation':
            df[f'{prefix}result_time'] = df.apply(
                lambda row: row[f'{prefix}result_time'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                axis=1
            )

        if component != 'ThingAssociation':

            df[f'{prefix}self_link'] = df.apply(
                lambda row: self.get_ref(
                    override_component=component,
                    entity_id=row[f'{prefix}id']
                ), axis=1
            )

            if (component_relations := getattr(component_schemas, f'{component}Relations', None)) is not None:
                for related_component in component_relations.__fields__.keys():
                    related_component_schema = component_relations.__fields__[related_component]
                    if related_component_schema.shape == SHAPE_LIST:
                        related_component_name = lookup_component(
                            related_component_schema.type_.__name__, 'camel_singular', 'camel_plural'
                        )
                    else:
                        related_component_name = related_component_schema.type_.__name__
                    if f'{related_component}_rel' not in df.columns and \
                            related_component_schema.type_.__name__ != parent_component:
                        df[f'{prefix}{related_component}_link'] = df.apply(
                            lambda row: self.get_ref(
                                entity_id=row[f'{prefix}id'],
                                related_component=related_component_name,
                                override_component=component
                            ), axis=1
                        )

        if prefix:
            df[f'{prefix[:-2]}_rel'] = df.apply(
                lambda row: {
                    col[len(prefix):]: row[col]
                    for col in df.columns if col.startswith(prefix)
                }, axis=1
            )

        return df

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

        response = {}

        if self.component in ['FeatureOfInterest', 'HistoricalLocation']:
            if count is True:
                response['count'] = 0
            response['values'] = []

            return response

        if top is None:
            if self.component == 'Observation':
                top = 1000
            else:
                top = 100

        if skip is None:
            skip = 0

        querysets = self.build_querysets(
            query_structure={
                'component': self.component,
                'count': count,
                'array': True,
                'select': None,
                'pagination': {'top': top, 'skip': skip},
                'filters': filters,
                'order_by': order_by,
                'children': expand if expand else []
            }
        )

        if count is True:
            response['count'] = querysets['count']

        dataframes = self.fetch_data(
            querysets=querysets
        )

        response_df = self.transform_dataframes(
            dataframes=dataframes
        )

        response['values'] = response_df.to_dict(orient='records')
        response['next_link'] = self.build_next_link(top, skip)

        return response

    def get(
            self,
            entity_id,
            expand
    ) -> Optional[dict]:
        """"""

        response = {}

        if self.component in ['FeatureOfInterest', 'HistoricalLocation']:
            return response

        querysets = self.build_querysets(
            query_structure={
                'component': self.component,
                'array': False,
                'pk': entity_id,
                'children': expand if expand else []
            }
        )

        dataframes = self.fetch_data(
            querysets=querysets
        )

        response_df = self.transform_dataframes(
            dataframes=dataframes
        )

        try:
            response = response_df.to_dict(orient='records')[0]
        except IndexError:
            return response

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
            grouped_observations = {}
            for entity_body in entity_bodies:
                grouped_observations[entity_body.datastream.id] = grouped_observations.get(
                    entity_body.datastream.id, []
                )
                grouped_observations[entity_body.datastream.id].append(entity_body)

            entities = core_models.Observation.objects.bulk_create(
                [
                    core_models.Observation(
                        id=uuid.uuid4(),
                        datastream_id=entity_body.datastream.id,
                        result=entity_body.result,
                        result_time=entity_body.result_time,
                        result_quality=entity_body.result_quality,
                        phenomenon_time=entity_body.phenomenon_time,
                        valid_begin_time=entity_body.valid_time,
                        valid_end_time=entity_body.valid_time,
                    ) for entity_body in [
                        observation for observations in grouped_observations.values() for observation in observations
                    ]
                ]
            )

            for datastream_id, observations in grouped_observations.items():
                datastream = core_models.Datastream.objects.get(pk=datastream_id)

                ds_result_end_time = datastream.result_end_time
                max_obs_result_time = max([
                    observation.result_time for observation in observations
                    if observation.result_time is not None
                ], default=None)

                if (
                        max_obs_result_time and ds_result_end_time and
                        max_obs_result_time.__datetime__() > ds_result_end_time
                   ) or (max_obs_result_time and not ds_result_end_time):
                    datastream.result_end_time = max_obs_result_time

                ds_result_begin_time = datastream.result_begin_time
                min_obs_result_time = min([
                    observation.result_time for observation in observations
                    if observation.result_time is not None
                ], default=None)

                if (
                        min_obs_result_time and ds_result_begin_time and
                        min_obs_result_time.__datetime__() < ds_result_begin_time
                   ) or (min_obs_result_time and not ds_result_begin_time):
                    datastream.result_begin_time = min_obs_result_time

                ds_phen_end_time = datastream.phenomenon_end_time
                max_obs_phen_time = max([
                    observation.phenomenon_time for observation in observations
                    if observation.phenomenon_time is not None
                ], default=None)

                if (
                        max_obs_phen_time and ds_phen_end_time and
                        max_obs_phen_time.__datetime__() > ds_phen_end_time
                   ) or (max_obs_phen_time and not ds_phen_end_time):
                    datastream.phenomenon_end_time = max_obs_phen_time

                ds_phen_start_time = datastream.phenomenon_start_time
                min_obs_phen_time = min([
                    observation.phenomenon_time for observation in observations
                    if observation.phenomenon_time is not None
                ], default=None)

                if (
                        min_obs_phen_time and ds_phen_start_time and
                        min_obs_phen_time.__datetime__() < ds_phen_start_time
                   ) or (min_obs_phen_time and not ds_phen_start_time):
                    datastream.phenomenon_start_time = min_obs_phen_time

                datastream.save()

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
            getattr(core_models, self.component).objects.get(pk=entity_id)
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

    @staticmethod
    def format_isointerval(start_time, end_time):
        """"""

        if pd.isnull(start_time) and pd.isnull(end_time):
            return None
        elif pd.isnull(start_time):
            return end_time.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif pd.isnull(end_time):
            return start_time.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return start_time.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def apply_order(query, order_by):
        """"""

        order_map = {
            'Datastreams/id': 'datastream_id'
        }

        query = query.order_by(*[
            (
                '-' if order_field['direction'] == 'desc' else '' +
                order_map.get(order_field['field'], order_field['field'])
            ) for order_field in order_by
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

    @staticmethod
    def apply_pagination(queryset, top, skip):
        """"""

        queryset = queryset[skip: skip+top]

        return queryset
