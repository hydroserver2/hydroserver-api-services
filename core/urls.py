from ninja import NinjaAPI
from django.urls import path
from core.endpoints.thing.views import router as thing_router
from core.endpoints.sensor.views import router as sensor_router
from core.endpoints.observedproperty.views import router as observed_property_router
from core.endpoints.processinglevel.views import router as processing_level_router
from core.endpoints.unit.views import router as unit_router
from core.endpoints.photo.views import router as photo_router
from core.endpoints.datastream.views import router as datastream_router
from core.endpoints.resultqualifier.views import router as result_qualifier_router
from core.endpoints.dataloader.views import router as data_loader_router
from core.endpoints.datasource.views import router as data_source_router

api = NinjaAPI(
    title='HydroServer Data Management API',
    version='0.0.1',
    urls_namespace='data'
)

thing_router.add_router('/{thing_id}/photos', photo_router)
api.add_router('/things', thing_router)
api.add_router('/datastreams', datastream_router)
api.add_router('/observed-properties', observed_property_router)
api.add_router('/processing-levels', processing_level_router)
api.add_router('/sensors', sensor_router)
api.add_router('/units', unit_router)
api.add_router('/result-qualifiers', result_qualifier_router)
api.add_router('/data-loaders', data_loader_router)
api.add_router('/data-sources', data_source_router)

urlpatterns = [
    path('', api.urls),
]
