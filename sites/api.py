from ninja import NinjaAPI

# from sites.endpoints.token import router as token_router
from sites.endpoints.datastream import router as datastream_router
from sites.endpoints.observed_property import router as op_router
from sites.endpoints.processing_level import router as pl_router
from sites.endpoints.sensor import router as sensor_router
from sites.endpoints.thing import router as thing_router
from sites.endpoints.unit import router as unit_router
# from sites.endpoints.user import router as user_router
from sites.endpoints.photo import router as photo_router
from sites.endpoints.data_loader import router as dl_router
from sites.endpoints.data_sources import router as ds_router

api = NinjaAPI()

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
