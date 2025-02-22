from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from hydroserver.views import index, load_test_data, load_default_data

urlpatterns = [
    path("admin/actions/load-test-data/", load_test_data, name="load_test_data"),
    path("admin/actions/load-default-data/", load_default_data, name="load_default_data"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("iam.urls")),
    path("api/", include("sta.urls")),
    path("", index)
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STORAGES["staticfiles"]["OPTIONS"]["location"])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.STORAGES["default"]["OPTIONS"]["location"])
