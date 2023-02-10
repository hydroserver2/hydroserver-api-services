from django.urls import path
from sensorthings.core import st_core_api
from sensorthings.mappers.api import build_api_extension
from sensorthings.mappers.odm2c import schemas as odm2c_schemas


st_odm2c_api = build_api_extension(
    api=st_core_api,
    title='HydroServer SensorThings API - ODM2c',
    namespace='odm2c',
    schemas=odm2c_schemas
)

urlpatterns = [
    path('v1.1/', st_core_api.urls)
]
