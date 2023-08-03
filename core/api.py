from ninja import NinjaAPI
from core.routers import thing_router
from core.auth.jwt import api as jwt_api


management_api = NinjaAPI(
    version='0.0.1',
    urls_namespace='management'
)


management_api.add_router(prefix='', router=thing_router)
