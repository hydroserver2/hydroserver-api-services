# from django.urls import path
# from django.views.decorators.csrf import ensure_csrf_cookie
# from sensorthings import SensorThingsAPI
# from sensorthings.extensions.dataarray import data_array_extension
# from sensorthings.extensions.qualitycontrol import quality_control_extension
# from stapi.api import hydroserver_extension
# from stapi.engine import HydroServerSensorThingsEngine
#
#
# st_api_1_1 = SensorThingsAPI(
#     title='HydroServer SensorThings API',
#     version='1.1',
#     description='This is the documentation for the HydroServer SensorThings API implementation.',
#     engine=HydroServerSensorThingsEngine,
#     extensions=[data_array_extension, quality_control_extension, hydroserver_extension],
#     docs_decorator=ensure_csrf_cookie,
#     csrf=True
# )
#
# urlpatterns = [
#     path('v1.1/', st_api_1_1.urls),
# ]
