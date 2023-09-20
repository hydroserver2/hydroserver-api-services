from ninja import NinjaAPI
from django.urls import path
from core.endpoints.data_loader import router as dl_router
from core.endpoints.data_sources import router as ds_router

from core.routers.thing.views import router as thing_router
from core.routers.sensor.views import router as sensor_router
from core.routers.observedproperty.views import router as observed_property_router
from core.routers.processinglevel.views import router as processing_level_router
from core.routers.unit.views import router as unit_router
from core.routers.photo.views import router as photo_router
from core.routers.datastream.views import router as datastream_router
from core.routers.resultqualifier.views import router as result_qualifier_router

api = NinjaAPI(
    title='HydroServer Data Management API',
    version='0.0.1',
    urls_namespace='data'
)

thing_router.add_router('/{thing_id}/photos', photo_router)
thing_router.add_router('/{thing_id}/datastreams', datastream_router)
api.add_router('/things', thing_router)
api.add_router('/observed-properties', observed_property_router)
api.add_router('/processing-levels', processing_level_router)
api.add_router('/sensors', sensor_router)
api.add_router('/units', unit_router)
api.add_router('/result-qualifiers', result_qualifier_router)
api.add_router('/data-loaders', dl_router)
api.add_router('/data-sources', ds_router)

urlpatterns = [
    path('', api.urls),
]
