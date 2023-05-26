import uuid
import numpy as np
import pandas as pd
from typing import List, Union, Tuple, Optional
from odata_query.django.django_q import AstToDjangoQVisitor
from odata_query.rewrite import AliasRewriter
from django.core.exceptions import ObjectDoesNotExist
from django.urls.exceptions import Http404
from django.db import connection
from django.db.models import F, Window
from django.db.models.functions import DenseRank
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

    # def get_fields(self, select=None, expand=None, component_override=None, prefix=''):
    #     """"""
    #
    #     component = component_override if component_override else self.component
    #
    #     if not expand:
    #         expand = []
    #
    #     if not sensorthings_mapper.get(component):
    #         return []
    #
    #     fields = [
    #         prefix + '__'.join(field) for field in sensorthings_mapper[component].get_output_paths(select)
    #     ]
    #
    #     extra_fields = [prefix + 'datastream_id'] if component == 'Observation' else []
    #
    #     nested_fields = [i for j in [
    #         self.get_fields(
    #             component_override=field['entity'],
    #             expand=[field['child']] if field['child'] else None,
    #             prefix=prefix + lookup_component(field['entity'], 'camel_singular', 'snake_singular') + '__'
    #         ) for field in expand
    #     ] for i in j]
    #
    #     return fields + extra_fields + nested_fields

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

    def get_related_fields(self, query_structure, prefix='', df_prefixes=None):
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
                child_related_fields, related_prefetch_components, df_prefixes = self.get_related_fields(
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
                prefetch_components.append({
                    'component': child_structure['component'],
                    'prefetch_filter': f'{prefix}id',
                    'query_structure': child_structure,
                    'prefetch_field': lookup_component(component, 'camel_singular', 'snake_singular') + '_id'
                })

        extra_fields = [prefix + 'datastream_id'] if component == 'Observation' else []

        return related_fields + extra_fields, prefetch_components, df_prefixes

    def build_orm_query(self, query_structure, prefetch_field=None, prefetch_filter=None):
        """"""

        component = query_structure['component']
        queryset = getattr(core_models, component).objects

        related_fields, prefetch_components, df_prefixes = self.get_related_fields(query_structure)

        queryset = queryset.values(*related_fields)

        if query_structure.get('order_by'):
            # queryset = self.apply_order(queryset, query_structure['order_by'])
            pass

        if query_structure.get('filters'):
            # queryset = self.apply_filters(queryset, query_structure['filters'])
            pass

        if query_structure.get('pagination'):
            # queryset = self.apply_pagination(queryset, query_structure['pagination'])
            pass

        prefetch_querysets = [
            self.build_orm_query(
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

    def run_queries(self, orm_query):

        query = orm_query['queryset']

        if orm_query.get('prefetch_field'):
            query = query.annotate(
                rank=Window(
                    expression=DenseRank(),
                    partition_by=F(orm_query['prefetch_field']),
                    order_by='pk'
                )
            )

            sql, params = query.query.sql_with_params()

            params = [
                f"'{param}'" if isinstance(param, uuid.UUID) else param for param in params
            ]

            rank_group_limit = 10
            total_query_limit = 100

            query = getattr(core_models, orm_query['component']).objects.raw("""
                SELECT * FROM ({}) ranked_result
                WHERE rank <= %s
                LIMIT %s
            """.format(sql), [*params, rank_group_limit, total_query_limit])

            df = pd.DataFrame(list(self.raw_query_to_dicts(str(query.query))))
            df = df.replace({np.nan: None})

        else:
            df = pd.DataFrame(list(query))

        child_dfs = []

        for prefetch in orm_query['prefetch']:
            prefetch['queryset'] = prefetch['queryset'].filter(
                **{f"{prefetch['prefetch_field']}__in": df[prefetch['prefetch_filter']].tolist()}
            )
            child_dfs.append(self.run_queries(prefetch))

        return {
            'df': df,
            'component': orm_query['component'],
            'prefetch_prefix': orm_query['prefetch_filter'][:-2] if orm_query['prefetch_filter'] else '',
            'df_prefixes': orm_query['df_prefixes'],
            'child_dfs': child_dfs
        }

    def transform_dataframes(self, dataframe_response):
        """"""

        df = dataframe_response['df']

        for df_prefix in dataframe_response['df_prefixes']:
            for child_df in [
                child_df for child_df in dataframe_response['child_dfs']
                if child_df['prefetch_prefix'] == df_prefix['prefix']
            ]:
                transformed_child_df = self.transform_dataframes(child_df)

                if child_df['component'] == 'ThingAssociation':
                    merged_field_name = 'thing_associations'
                else:
                    merged_field_name = lookup_component(child_df['component'], 'camel_singular', 'snake_plural')
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

            df = self.transform_response(df, df_prefix['component'], df_prefix['prefix'])

        return df

    def merge_dataframes(
            self,
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
            right_on=child_merge_group_column
        )



        return parent_df


    def transform_response(self, response_df, component, prefix):
        """"""

        if component == 'Thing':
            response_df[f'{prefix}properties'] = response_df.apply(
                lambda row: {
                    'sampling_feature_code': row[f'{prefix}sampling_feature_code'],
                    'sampling_feature_type': row[f'{prefix}sampling_feature_type'],
                    'site_type': row[f'{prefix}site_type'],
                    'contact_people': row[f'{prefix}thing_associations']
                }, axis=1
            )
        elif self.component == 'Location':
            response_df = response_df.rename(columns={
                f'{prefix}thing_id': f'{prefix}id'
            })
            response_df[f'{prefix}location'] = response_df.apply(
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
            response_df[f'{prefix}properties'] = response_df.apply(
                lambda row: {
                    'city': row[f'{prefix}city'],
                    'state': row[f'{prefix}state'],
                    'county': row[f'{prefix}country'],
                    'elevation': row[f'{prefix}elevation'],
                    'elevation_datum': row[f'{prefix}elevation_datum']
                }, axis=1
            )
        elif component == 'ObservedProperty':
            response_df[f'{prefix}properties'] = response_df.apply(
                lambda row: {
                    'variable_code': row[f'{prefix}variable_code'],
                    'variable_type': row[f'{prefix}variable_type']
                }, axis=1
            )
        elif self.component == 'Sensor':
            response_df[f'{prefix}sensor_metadata'] = response_df.apply(
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
            response_df[f'{prefix}unit_of_measurement'] = response_df.apply(
                lambda row: {
                    'name': row[f'{prefix}unit__name'],
                    'symbol': row[f'{prefix}unit__symbol'],
                    'definition': row[f'{prefix}unit__definition']
                }, axis=1
            )
            response_df[f'{prefix}properties'] = response_df.apply(
                lambda row: {
                    'result_type': row[f'{prefix}result_type'],
                    'status': row[f'{prefix}status'],
                    'sampled_medium': row[f'{prefix}sampled_medium'],
                    'value_count': row[f'{prefix}value_count'] if not pd.isnull(row[f'{prefix}value_count']) else 0,
                    'no_data_value': row[f'{prefix}no_data_value'],
                    'processing_level_code': row[f'{prefix}processing_level__processing_level_code'],
                    # 'intended_time_spacing': row[f'{prefix}intended_time_spacing'],
                    'intended_time_spacing_unit_of_measurement': {
                        'name': row[f'{prefix}intended_time_spacing_units__name'],
                        'symbol': row[f'{prefix}intended_time_spacing_units__symbol'],
                        'definition': row[f'{prefix}intended_time_spacing_units__definition']
                    },
                    'aggregation_statistic': row[f'{prefix}aggregation_statistic'],
                    # 'time_aggregation_interval': row[f'{prefix}time_aggregation_interval'],
                    'time_aggregation_interval_unit_of_measurement': {
                        'name': row[f'{prefix}time_aggregation_interval_units__name'],
                        'symbol': row[f'{prefix}time_aggregation_interval_units__symbol'],
                        'definition': row[f'{prefix}time_aggregation_interval_units__definition']
                    },
                    'phenomenon_time': self.format_isointerval(
                        row[f'{prefix}phenomenon_start_time'], row[f'{prefix}phenomenon_end_time']
                    ),
                    'result_time': self.format_isointerval(
                        row[f'{prefix}result_begin_time'], row[f'{prefix}result_end_time']
                    )
                }, axis=1
            )
        elif self.component == 'Observation':
            response_df[f'{prefix}result_time'] = response_df.apply(
                lambda row: row[f'{prefix}result_time'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                axis=1
            )

        if prefix:
            response_df[prefix[:-2]] = response_df.apply(
                lambda row: {
                    col[len(prefix):]: row[col]
                    for col in response_df.columns if col.startswith(prefix)
                }, axis=1
            )

        return response_df

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

        # if hasattr(core_models, self.component):
        #     query = getattr(core_models, self.component).objects
        # else:
        #     query = core_models.Thing.objects.none()

        response = {}

        orm_query = self.build_orm_query(
            query_structure={
                'component': self.component,
                'array': True,
                'select': None,
                'pagination': None,
                'filters': filters,
                'order_by': order_by,
                'children': expand if expand else []
            }
        )

        dataframe_response = self.run_queries(
            orm_query=orm_query
        )

        response_dict = self.transform_dataframes(
            dataframe_response=dataframe_response
        )

        response_json = response_dict.to_dict(orient='records')

        return {
            'value': response_json
        }


        if filters is not None:
            query = self.apply_filters(query, filters)

        response_count = self.get_count(query)

        if order_by is not None:
            query = self.apply_order(query, order_by)

        if count is True:
            response['count'] = response_count

        if top is None:
            if self.component == 'Observation':
                top = 1000
            else:
                top = 100

        if skip is None:
            skip = 0

        fields = self.get_fields(select, expand)

        queryset = query.values(*fields)
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

        response_value[0]['thing'] = {'name': 'hello'}
        response_value[0]['sensor'] = {'name': 'some_sensor'}

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
            return end_time.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif pd.isnull(end_time):
            return start_time.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return start_time.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end_time.strftime('%Y-%m-%dT%H:%M:%SZ')


    def transform_response_old(self, response_df):
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
                lambda row: row['result_time'].strftime('%Y-%m-%dT%H:%M:%SZ'),
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
