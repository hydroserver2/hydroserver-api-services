from ninja import NinjaAPI
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from sensorthings import SensorThingsAPI
from sensorthings.extensions.dataarray import data_array_extension
from sensorthings.extensions.qualitycontrol import quality_control_extension
from hydroserver import __version__
from hydroserver.renderer import ORJSONRenderer
from sta.api import hydroserver_extension
from sta.services.sensorthings import HydroServerSensorThingsEngine
from sta.views import (
    thing_router,
    tag_router,
    tag_key_router,
    photo_router,
    observed_property_router,
    processing_level_router,
    result_qualifier_router,
    sensor_router,
    unit_router,
    datastream_router,
    sta_vocabulary_router,
)
from etl.views import (
    orchestration_system_router,
    data_source_router,
    data_archive_router,
    hydroshare_archival_router,
)


data_api = NinjaAPI(
    title="HydroServer Data Management API",
    version=__version__,
    urls_namespace="data",
    docs_decorator=ensure_csrf_cookie,
    renderer=ORJSONRenderer(),
)

thing_router.add_router("{thing_id}/tags", tag_router)
thing_router.add_router("{thing_id}/photos", photo_router)
thing_router.add_router("{thing_id}/archive", hydroshare_archival_router)
data_api.add_router("things", thing_router)
data_api.add_router("tags", tag_key_router)
data_api.add_router("observed-properties", observed_property_router)
data_api.add_router("processing-levels", processing_level_router)
data_api.add_router("result-qualifiers", result_qualifier_router)
data_api.add_router("sensors", sensor_router)
data_api.add_router("units", unit_router)
data_api.add_router("datastreams", datastream_router)
data_api.add_router("vocabulary", sta_vocabulary_router)

data_api.add_router("orchestration-systems", orchestration_system_router)
data_api.add_router("data-sources", data_source_router)
data_api.add_router("data-archives", data_archive_router)

st_api_1_1 = SensorThingsAPI(
    title="HydroServer SensorThings API",
    version="1.1",
    description="This is the documentation for the HydroServer SensorThings API implementation.",
    engine=HydroServerSensorThingsEngine,
    extensions=[data_array_extension, quality_control_extension, hydroserver_extension],
    docs_decorator=ensure_csrf_cookie,
)

urlpatterns = [
    path("data/", data_api.urls),
    path("sensorthings/v1.1/", st_api_1_1.urls),
]
