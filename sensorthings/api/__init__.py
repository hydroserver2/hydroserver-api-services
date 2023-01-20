from ninja import NinjaAPI, Router
from django.conf import settings

from sensorthings.api.components.root.views import router as root_router
from sensorthings.api.components.datastreams.views import router as datastreams_router
from sensorthings.api.components.featuresofinterest.views import router as featuresofinterest_router
from sensorthings.api.components.historicallocations.views import router as historicallocations_router
from sensorthings.api.components.locations.views import router as locations_router
from sensorthings.api.components.observations.views import router as observations_router
from sensorthings.api.components.observedproperties.views import router as observedproperties_router
from sensorthings.api.components.sensors.views import router as sensors_router
from sensorthings.api.components.things.views import router as things_router


api_router = Router()

api_router.add_router('', datastreams_router)
api_router.add_router('', featuresofinterest_router)
api_router.add_router('', historicallocations_router)
api_router.add_router('', locations_router)
api_router.add_router('', observations_router)
api_router.add_router('', observedproperties_router)
api_router.add_router('', sensors_router)
api_router.add_router('', things_router)

api = NinjaAPI(**settings.ST_API)

api.add_router('', root_router)
api.add_router(f'v{settings.ST_VERSION}/', api_router)
