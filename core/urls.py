from ninja import NinjaAPI
from django.urls import path

# from sites.endpoints.token import router as token_router
from core.endpoints.datastream import router as datastream_router
from core.endpoints.observed_property import router as op_router
from core.endpoints.processing_level import router as pl_router
from core.endpoints.sensor import router as sensor_router
from core.endpoints.thing import router as thing_router
from core.endpoints.unit import router as unit_router
# from core.endpoints.user import router as user_router
from core.endpoints.photo import router as photo_router
from core.endpoints.data_loader import router as dl_router
from core.endpoints.data_sources import router as ds_router

api = NinjaAPI(
    title='HydroServer Data Management API',
    version='0.0.1',
    urls_namespace='data'
)

# api.add_router("/token", token_router)
api.add_router("/datastreams", datastream_router)
api.add_router("/observed-properties", op_router)
api.add_router("/processing-levels", pl_router)
api.add_router("/sensors", sensor_router)
api.add_router("/things", thing_router)
api.add_router("/units", unit_router)
# api.add_router("/user", user_router)
api.add_router("/photos", photo_router)
api.add_router("/data-loaders", dl_router)
api.add_router("/data-sources", ds_router)

urlpatterns = [
    path('', api.urls),
]
