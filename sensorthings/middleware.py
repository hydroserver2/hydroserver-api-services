import inflection
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, ResolverMatch
from django.urls.exceptions import Http404
from django.conf import settings
from django.http import HttpRequest
from sensorthings import api as sta
from sensorthings.api.core.main import SensorThings


class SensorThingsRouter(MiddlewareMixin):
    st_components = [
        capability['SINGULAR_NAME'] for capability in settings.ST_CAPABILITIES
    ]

    def process_request(self, request: HttpRequest) -> None:
        """
        Middleware for resolving nested components in URLs.

        :param request: Django HttpRequest object.
        :return: None
        """

        if request.path_info.startswith(f'/{settings.ST_PREFIX}/'):
            resolved_path = resolve(request.path_info)

            if resolved_path.url_name is not None:
                request.entity = self.resolve_simple_entity(resolved_path)
            elif resolved_path.url_name is None and request.method == 'GET':
                request.entity = self.resolve_nested_entity(request)
            else:
                request.entity = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for initializing a datastore engine for the request.

        :param request: Django HttpRequest object.
        :param view_func: The view function associated with this request.
        :param view_args: The arguments that will be passed to the view function.
        :param view_kwargs: The keyword arguments that will be passed to the view function.
        :return: None
        """

        if hasattr(request, 'entity') and request.entity is not None:
            request.engine = SensorThings(
                host=request.get_host(),
                path=request.path_info,
                entity=request.entity
            )
        else:
            request.engine = None

    def resolve_simple_entity(self, resolved_path: ResolverMatch) -> str | None:
        """
        Resolves simple un-nested URLs and returns the associated SensorThings entity.

        :param resolved_path: Django ResolverMatch object.
        :return: One of ST_ENTITY.
        """

        entity = inflection.camelize(resolved_path.url_name.split('_', 1)[-1])

        if entity in self.st_components:
            return entity

    def resolve_nested_entity(self, request: HttpRequest) -> str | None:
        """
        Resolves complex nested URLs, updates request.path_info, and returns the associated SensorThings entity.

        :param request: Django HttpRequest object.
        :return: One of ST_ENTITY.
        """

        path_components = request.path_info.split('/')[3:]
        path_prefix = '/'.join(request.path_info.split('/')[:3])
        previous_component = None
        endpoint = None
        entity = None

        for i, raw_component in enumerate(path_components):
            path = f'{path_prefix}/{raw_component}'
            resolved_path = resolve(path)

            if isinstance(resolved_path.url_name, str) and resolved_path.url_name.startswith('list'):
                prop_name = resolved_path.url_name.replace('list_', '')
                component = inflection.camelize(prop_name)
                entity = component
                endpoint = f'{path_prefix}/{raw_component}'
            elif isinstance(resolved_path.url_name, str) and resolved_path.url_name.startswith('get'):
                prop_name = resolved_path.url_name.replace('get_', '')
                component = inflection.camelize(prop_name)
                entity = component
                endpoint = f'{path_prefix}/{raw_component}'
            elif resolved_path.url_name is None and raw_component in self.st_components:
                prop_name = inflection.underscore(raw_component)
                component = inflection.camelize(prop_name)
                entity = component
                if component == 'FeatureOfInterest':
                    endpoint = f'{path_prefix}/FeaturesOfInterest(1)'
                else:
                    endpoint = f'{path_prefix}/{inflection.pluralize(raw_component)}(1)'
            else:
                prop_name = inflection.underscore(raw_component)
                component = raw_component

            if previous_component and previous_component in self.st_components:
                if prop_name not in getattr(sta, previous_component).__fields__:
                    raise Http404
            elif previous_component in ['$value', '$ref']:
                raise Http404
            elif component == '$value':
                pass
            elif component == '$ref':
                pass
            else:
                pass

            previous_component = component

        if endpoint:
            request.path_info = endpoint

        if entity in self.st_components:
            return entity
