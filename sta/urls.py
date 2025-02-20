from ninja import NinjaAPI
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from hydroserver import __version__
from sta.views import (thing_router, tag_router, tag_key_router, photo_router, observed_property_router,
                       processing_level_router, result_qualifier_router, sensor_router, unit_router, datastream_router)


data_api = NinjaAPI(
    title="HydroServer Data Management API",
    version=__version__,
    urls_namespace="data",
    docs_decorator=ensure_csrf_cookie
)

thing_router.add_router("{thing_id}/tags", tag_router)
thing_router.add_router("{thing_id}/photos", photo_router)
data_api.add_router("things", thing_router)
data_api.add_router("tags", tag_key_router)
data_api.add_router("observed-properties", observed_property_router)
data_api.add_router("processing-levels", processing_level_router)
data_api.add_router("result-qualifiers", result_qualifier_router)
data_api.add_router("sensors", sensor_router)
data_api.add_router("units", unit_router)
data_api.add_router("datastreams", datastream_router)

urlpatterns = [
    path("", data_api.urls),
]
