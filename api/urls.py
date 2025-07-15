from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from sensorthings import SensorThingsAPI
from sensorthings.extensions.dataarray import data_array_extension
from hydroserver import __version__
from api.renderer import ORJSONRenderer
from sta.api import hydroserver_extension
from sta.services.sensorthings import HydroServerSensorThingsEngine
from iam.views import workspace_router, role_router
from sta.views import (
    thing_router,
    observed_property_router,
    processing_level_router,
    result_qualifier_router,
    sensor_router,
    unit_router,
    datastream_router,
    observation_router,
)
from etl.views import (
    hydroshare_archival_router,
    orchestration_system_router,
    data_source_router,
    data_archive_router,
)


api = NinjaAPI(
    title="HydroServer Data Management API",
    version=__version__,
    urls_namespace="data",
    docs_decorator=ensure_csrf_cookie,
    renderer=ORJSONRenderer(),
    throttle=[
        AnonRateThrottle("20/s"),
        AuthRateThrottle("20/s"),
    ],
)

thing_router.add_router("{thing_id}/archive", hydroshare_archival_router)
datastream_router.add_router("{datastream_id}/observations", observation_router)

api.add_router("workspaces", workspace_router)
api.add_router("roles", role_router)

api.add_router("things", thing_router)
api.add_router("datastreams", datastream_router)
api.add_router("observed-properties", observed_property_router)
api.add_router("units", unit_router)
api.add_router("sensors", sensor_router)
api.add_router("processing-levels", processing_level_router)
api.add_router("result-qualifiers", result_qualifier_router)

api.add_router("orchestration-systems", orchestration_system_router)
api.add_router("data-sources", data_source_router)
api.add_router("data-archives", data_archive_router)

st_api_1_1 = SensorThingsAPI(
    title="HydroServer SensorThings API",
    version="1.1",
    description="This is the documentation for the HydroServer SensorThings API implementation.",
    engine=HydroServerSensorThingsEngine,
    extensions=[data_array_extension, hydroserver_extension],
    docs_decorator=ensure_csrf_cookie,
    throttle=[
        AnonRateThrottle("20/s"),
        AuthRateThrottle("20/s"),
    ],
)

urlpatterns = [
    path("data/", api.urls),
    path("sensorthings/v1.1/", st_api_1_1.urls),
]
