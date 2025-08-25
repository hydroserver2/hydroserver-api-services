from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from web.views import index


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("iam.urls")),
    path("api/", include("api.urls")),
]

urlpatterns += [
    re_path(r"^(?!admin/|accounts/|api/|static/|media/).*$", index),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STORAGES["staticfiles"]["OPTIONS"]["location"],
)
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.STORAGES["default"]["OPTIONS"]["location"],
)
