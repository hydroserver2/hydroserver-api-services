import uuid
import pandas as pd
from typing import List
from django.core.exceptions import ObjectDoesNotExist
from django.urls.exceptions import Http404
from hydrothings import SensorThingsAbstractEngine
from sites import models as core_models


class SensorThingsEngine(SensorThingsAbstractEngine):

    mapping = {
        'Thing': {
            'id': 'thing__id',
            'name': 'thing__name',
            'description': 'thing__description',
            'properties': [
                'thing__sampling_feature_code',
                'thing__sampling_feature_type',
                'thing__site_type',
                'person__first_name',
                'person__last_name',
                'person__email',
                'person__organization',
                'person__phone'
            ]
        },
        'Location': {
            'id': 'thing_id',
            'name': 'name',
            'description': 'description',
            'encoding_type': 'encoding_type',
            'location': [
                'latitude',
                'longitude'
            ],
            'properties': [
                'city',
                'state',
                'country',
                'elevation_m',
                'elevation_datum'
            ]
        },
        'HistoricalLocation': {},
        'Sensor': {
            'id': 'id',
            'name': 'name',
            'description': 'description',
            'encoding_type': 'encoding_type',
            'sensor_metadata': [
                'method_code',
                'method_type',
                'method_link',
                'manufacturer',
                'model',
                'model_url'
            ]
        },
        'ObservedProperty': {
            'id': 'id',
            'name': 'name',
            'definition': 'definition',
            'description': 'description',
            'properties': [
                'variable_code',
                'variable_type'
            ]
        },
        'Datastream': {
            'id': 'id',
            'name': 'name',
            'description': 'description',
            'unit_of_measurement': [
                'unit__name',
                'unit__definition',
                'unit__symbol'
            ],
            'observation_type': 'observation_type',
            'properties': [
                'result_type',
                'status',
                'sampled_medium',
                'value_count',
                'no_data_value',
                'processing_level__processing_level_code',
                'intended_time_spacing',
                'intended_time_spacing_units__name',
                'intended_time_spacing_units__definition',
                'intended_time_spacing_units__symbol',
                'aggregation_statistic',
                'time_aggregation_interval',
                'time_aggregation_interval_units__name',
                'time_aggregation_interval_units__definition',
                'time_aggregation_interval_units__symbol',
            ],
            'phenomenon_time': [
                'phenomenon_start_time',
                'phenomenon_end_time'
            ],
            'result_time': [
                'result_begin_time',
                'result_end_time'
            ]
        },
        'Observation': {
            'id': 'id',
            'result': 'result',
            'result_time': 'result_time',
            'result_quality': 'result_quality',
            'phenomenon_time': 'phenomenon_time',
            'valid_time': [
                'valid_begin_time',
                'valid_end_time'
            ]
        },
        'FeatureOfInterest': {}
    }

    def __init__(self, host: str, scheme: str, path: str, version: str, component: str, component_path: str):
        self.host = host
        self.scheme = scheme
        self.path = path
        self.component = component

    def get_fields(self, select=None):
        """"""

        return [
            field for fields in [
                db_field if isinstance(db_field, list) else [db_field]
                for st_field, db_field in self.mapping[self.component].items()
                if not select or st_field in select
            ] for field in fields
        ]

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

        # if filter is not None:
        #     query = self.apply_filters(query, filter)

        response_count = self.get_count(query)

        # if order_by is not None:
        #     query = self.apply_order(query, order_by)

        # if expand is not None:
        #     query = self.apply_expand(query, expand)

        if count is True:
            response['count'] = response_count

        queryset = query.values(*self.get_fields(select))

        # if top is not None or skip != 0:
        #     queryset = self.apply_pagination(queryset, top, skip)

        response_df = pd.DataFrame(list(queryset))
        response_df = self.transform_response(response_df)

        response_value = response_df.to_dict('records')

        response_value = self.build_related_links(response_value, is_collection=True)
        response_value = self.build_self_links(response_value, is_collection=True)

        response['value'] = response_value

        return response

    def get(
            self,
            entity_id
    ) -> dict:
        """"""

        if self.component == 'Thing':
            query = core_models.ThingAssociation.objects
            query = query.filter(thing__id=entity_id)
        else:
            query = getattr(core_models, self.component).objects
            query = query.filter(pk=entity_id)

        queryset = query.values(*self.get_fields())

        response_df = pd.DataFrame(list(queryset))
        response_df = self.transform_response(response_df)

        try:
            response = response_df.to_dict('records')[0]
        except IndexError:
            response = {}

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

    def transform_response(self, response_df):
        """"""

        if self.component == 'Thing':
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
                    'elevation_m': row['elevation_m'],
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
                    'value_count': row['value_count'],
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
                    'phenomenon_time': row['phenomenon_start_time'],
                    'result_time': row['result_begin_time']
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
