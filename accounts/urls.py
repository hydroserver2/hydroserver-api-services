from django.urls import path
from ninja_extra import NinjaExtraAPI
from accounts.endpoints.user.views import user_router
from accounts.endpoints.apikey.views import api_key_router
from accounts.endpoints.oauth.views.google import google_router
from accounts.endpoints.oauth.views.orcid import orcid_router
from accounts.endpoints.oauth.views.hydroshare import hydroshare_router
from accounts.endpoints.jwt.views import HydroServerJWTController
from hydroserver import settings


accounts_api = NinjaExtraAPI(
    title='HydroServer Account Management API',
    version='0.0.1',
    urls_namespace='accounts'
)


accounts_api.add_router(prefix='', router=user_router)
accounts_api.add_router(prefix='api-keys', router=api_key_router)
accounts_api.register_controllers(HydroServerJWTController)

if not settings.DISABLE_ACCOUNT_CREATION:
    if settings.AUTHLIB_OAUTH_CLIENTS.get('google', {}).get('client_id'):
        accounts_api.add_router(prefix='google', router=google_router)

    if settings.AUTHLIB_OAUTH_CLIENTS.get('orcid', {}).get('client_id'):
        accounts_api.add_router(prefix='orcid', router=orcid_router)

    if settings.AUTHLIB_OAUTH_CLIENTS.get('hydroshare', {}).get('client_id'):
        accounts_api.add_router(prefix='hydroshare', router=hydroshare_router)

urlpatterns = [
    path('', accounts_api.urls),
]
