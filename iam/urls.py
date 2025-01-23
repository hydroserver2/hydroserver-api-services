from ninja import NinjaAPI
from django.urls import path
from hydroserver import __version__
from iam.views import profile_router, type_router, get_auth_methods


iam_api = NinjaAPI(
    title="HydroServer Identity and Access Management API",
    version=__version__,
    urls_namespace="iam"
)

iam_api.add_router("/profile", profile_router)
iam_api.add_router("/types", type_router)

urlpatterns = [
    path("", iam_api.urls),
    path("authentication/methods", get_auth_methods, name="auth_methods"),
]
