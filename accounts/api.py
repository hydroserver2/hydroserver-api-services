from ninja import NinjaAPI
from accounts.views import router


user_api = NinjaAPI(
    title='HydroServer User Management API',
    version='0.0.1',
    urls_namespace='user'
)

user_api.add_router(prefix='', router=router)
