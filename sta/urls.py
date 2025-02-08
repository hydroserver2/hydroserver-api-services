from ninja import NinjaAPI
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from hydroserver import __version__
from sta.views import (thing_router, tag_router, photo_router)


data_api = NinjaAPI(
    title="HydroServer Data Management API",
    version=__version__,
    urls_namespace="data",
    docs_decorator=ensure_csrf_cookie,
    csrf=True
)

thing_router.add_router("{thing_id}/tags", tag_router)
thing_router.add_router("{thing_id}/photos", photo_router)
data_api.add_router("things", thing_router)

urlpatterns = [
    path("", data_api.urls),
]
