from ninja import NinjaAPI
from django.urls import path
from core.api.thing.views import router as thing_router
from core.api.sensor.views import router as sensor_router
from core.api.observedproperty.views import router as observed_property_router
from core.api.processinglevel.views import router as processing_level_router
from core.api.unit.views import router as unit_router
from core.api.photo.views import router as photo_router
from core.api.datastream.views import router as datastream_router
from core.api.resultqualifier.views import router as result_qualifier_router
from core.api.dataloader.views import router as data_loader_router
from core.api.datasource.views import router as data_source_router

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
