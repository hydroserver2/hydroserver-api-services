from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from hydroserver.views import index, spa_router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("iam.urls")),
    path("api/", include("sta.urls")),
    path("", index),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STORAGES["staticfiles"]["OPTIONS"]["location"],
)
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.STORAGES["default"]["OPTIONS"]["location"],
)

if settings.STORAGES.get("web"):
    urlpatterns += static(
        settings.WEB_URL,
        document_root=settings.STORAGES["web"]["OPTIONS"]["location"],
    )
    urlpatterns.append(re_path(r"^(?P<path>.*)$", spa_router))
