from ninja import NinjaAPI
from django.conf import settings

from sensorthings.core.components.root.views import router as root_router
from sensorthings.core.components.datastreams.views import router as datastreams_router
from sensorthings.core.components.featuresofinterest.views import router as featuresofinterest_router
from sensorthings.core.components.historicallocations.views import router as historicallocations_router
from sensorthings.core.components.locations.views import router as locations_router
from sensorthings.core.components.observations.views import router as observations_router
from sensorthings.core.components.observedproperties.views import router as observedproperties_router
from sensorthings.core.components.sensors.views import router as sensors_router
from sensorthings.core.components.things.views import router as things_router


st_core_api = NinjaAPI(**settings.ST_API)

st_core_api.add_router('', root_router)
st_core_api.add_router('', datastreams_router)
st_core_api.add_router('', featuresofinterest_router)
st_core_api.add_router('', historicallocations_router)
st_core_api.add_router('', locations_router)
st_core_api.add_router('', observations_router)
st_core_api.add_router('', observedproperties_router)
st_core_api.add_router('', sensors_router)
st_core_api.add_router('', things_router)
