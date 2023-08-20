from ninja_extra import NinjaExtraAPI
from accounts.views.users import user_router
from accounts.views.oauth import orcid_router, google_router
from accounts.views.jwt import HydroServerJWTController


accounts_api = NinjaExtraAPI(
    title='HydroServer Account Management API',
    version='0.0.1',
    urls_namespace='accounts'
)


accounts_api.add_router(prefix='', router=user_router)
accounts_api.register_controllers(HydroServerJWTController)
accounts_api.add_router(prefix='google', router=google_router)
accounts_api.add_router(prefix='orcid', router=orcid_router)
