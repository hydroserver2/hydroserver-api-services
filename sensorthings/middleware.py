import inflection
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.urls.exceptions import Resolver404, Http404
from django.apps import apps
from sensorthings import api as sta


class SensorThingsRouter(MiddlewareMixin):
    ST_ENTITIES = [
        'DataStream',
        'FeatureOfInterest',
        'HistoricalLocation',
        'Location',
        'Observation',
        'ObservedProperty',
        'Sensor',
        'Thing'
    ]

    def process_request(self, request) -> None:
        """"""

        if request.path_info.startswith(f'/{apps.get_app_config("sensorthings").api_prefix}/'):
            path_entities = request.path_info.split('/')[3:]
            path_prefix = '/'.join(request.path_info.split('/')[:3])
            previous_entity = None
            endpoint = None

            for i, raw_entity in enumerate(path_entities):
                path = f'{path_prefix}/{raw_entity}'
                resolved_path = resolve(path)

                if resolved_path.url_name and resolved_path.url_name.startswith('list'):
                    prop_name = resolved_path.url_name.replace('list_', '')
                    entity = inflection.camelize(prop_name)
                    endpoint = f'{path_prefix}/{raw_entity}'
                elif resolved_path.url_name and resolved_path.url_name.startswith('get'):
                    prop_name = resolved_path.url_name.replace('get_', '')
                    entity = inflection.camelize(prop_name)
                    endpoint = f'{path_prefix}/{raw_entity}'
                elif resolved_path.url_name is None and raw_entity in self.ST_ENTITIES:
                    prop_name = inflection.underscore(raw_entity)
                    entity = inflection.camelize(prop_name)
                    if entity == 'FeatureOfInterest':
                        endpoint = f'{path_prefix}/FeaturesOfInterest(1)'
                    else:
                        endpoint = f'{path_prefix}/{inflection.pluralize(raw_entity)}(1)'
                else:
                    prop_name = inflection.underscore(raw_entity)
                    entity = raw_entity

                if previous_entity and previous_entity in self.ST_ENTITIES:
                    if prop_name not in getattr(sta, previous_entity).__fields__:
                        raise Http404
                elif previous_entity in ['$value', '$ref']:
                    raise Http404
                elif entity == '$value':
                    pass
                elif entity == '$ref':
                    pass
                else:
                    pass

                previous_entity = entity

            if endpoint:
                request.path_info = endpoint



            # try:
            #     resolve(request.path_info)
            # except Resolver404:
            #     request.path_info = '/'.join(request.path_info.split('/')[:3] + request.path_info.split('/')[-2:])
