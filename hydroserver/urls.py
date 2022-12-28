from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.apps import apps


urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{apps.get_app_config("sensorthings").api_prefix}/', include('sensorthings.urls')),
    path('', include('sites.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)