from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from hydroserver import __version__
from hydroserver.renderer import ORJSONRenderer
from iam.views import (
    account_router,
    session_router,
    email_router,
    password_router,
    provider_router,
    get_auth_methods,
    workspace_router,
    role_router,
    collaborator_router,
    api_key_router,
    iam_vocabulary_router,
)


iam_api = NinjaAPI(
    title="HydroServer Identity and Access Management API",
    version=__version__,
    urls_namespace="iam",
    docs_decorator=ensure_csrf_cookie,
    renderer=ORJSONRenderer(),
    throttle=[
        AnonRateThrottle("20/s"),
        AuthRateThrottle("20/s"),
    ],
)

account_router.add_router("email", email_router)
account_router.add_router("password", password_router)
workspace_router.add_router("{workspace_id}/roles", role_router)
workspace_router.add_router("{workspace_id}/collaborators", collaborator_router)
workspace_router.add_router("{workspace_id}/api-keys", api_key_router)
iam_api.add_router("{client}/account", account_router)
iam_api.add_router("{client}/session", session_router)
iam_api.add_router("{client}/provider", provider_router)
iam_api.add_router("workspaces", workspace_router)
iam_api.add_router("vocabulary", iam_vocabulary_router)

urlpatterns = [
    path("", iam_api.urls),
    path("methods", get_auth_methods, name="auth_methods"),
]
