from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.apps import apps


class SensorThingsRouter(MiddlewareMixin):

    def process_request(self, request):
        if request.path_info.startswith(f'/{apps.get_app_config("sensorthings").api_prefix}/'):
            try:
                resolve(request.path_info)
            except Resolver404:
                request.path_info = '/'.join(request.path_info.split('/')[:3] + request.path_info.split('/')[-2:])
