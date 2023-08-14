from ninja import NinjaAPI
from ninja_extra import NinjaExtraAPI
from core.routers import thing_router, sensor_router
from core.auth.jwt import HydroServerJWTController
from core.auth.oauth import google_router, orcid_router


management_api = NinjaAPI(
    title='HydroServer Data Management API',
    version='0.0.1',
    urls_namespace='management'
)

management_api.add_router(prefix='', router=thing_router)
management_api.add_router(prefix='', router=sensor_router)

auth_api = NinjaAPI(
    title='HydroServer Authentication API',
    version='0.0.1',
    urls_namespace='auth',
    csrf=True
)

# auth_api.register_controllers(HydroServerJWTController)
auth_api.add_router(prefix='orcid', router=orcid_router)
auth_api.add_router(prefix='google', router=google_router)
