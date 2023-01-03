from ninja import NinjaAPI
from django.contrib.admin.views.decorators import staff_member_required
from .datastreams.views import router as datastreams_router
from .featuresofinterest.views import router as featuresofinterest_router
from .historicallocations.views import router as historicallocations_router
from .locations.views import router as locations_router
from .observations.views import router as observations_router
from .observedproperties.views import router as observedproperties_router
from .sensors.views import router as sensors_router
from .things.views import router as things_router


api = NinjaAPI(
    title='HydroServer SensorThings API',
    version='1.1',
    description='''
        The HydroServer API can be used to create and update monitoring site metadata, and post  
        results data to HydroServer data stores.
    ''',
    csrf=True,
    docs_decorator=staff_member_required
)

api.add_router('', datastreams_router)
api.add_router('', featuresofinterest_router)
api.add_router('', historicallocations_router)
api.add_router('', locations_router)
api.add_router('', observations_router)
api.add_router('', observedproperties_router)
api.add_router('', sensors_router)
api.add_router('', things_router)
