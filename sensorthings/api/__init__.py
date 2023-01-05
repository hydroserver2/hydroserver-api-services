from ninja import NinjaAPI, Router
from django.conf import settings
from .root.views import router as root_router
from .datastreams.views import router as datastreams_router
from .featuresofinterest.views import router as featuresofinterest_router
from .historicallocations.views import router as historicallocations_router
from .locations.views import router as locations_router
from .observations.views import router as observations_router
from .observedproperties.views import router as observedproperties_router
from .sensors.views import router as sensors_router
from .things.views import router as things_router


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
