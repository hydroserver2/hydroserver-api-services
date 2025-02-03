from ninja import NinjaAPI
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from hydroserver import __version__
from iam.views import (account_router, session_router, email_router, password_router, provider_router, get_auth_methods,
                       workspace_router, role_router)


iam_api = NinjaAPI(
    title="HydroServer Identity and Access Management API",
    version=__version__,
    urls_namespace="iam",
    docs_decorator=ensure_csrf_cookie,
    csrf=True
)

account_router.add_router("email", email_router)
account_router.add_router("password", password_router)
workspace_router.add_router("{workspace_id}/roles", role_router)
iam_api.add_router("{client}/account", account_router)
iam_api.add_router("{client}/session", session_router)
iam_api.add_router("{client}/provider", provider_router)
iam_api.add_router("workspaces", workspace_router)

urlpatterns = [
    path("", iam_api.urls),
    path("methods", get_auth_methods, name="auth_methods"),
]
