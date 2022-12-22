from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from datamanagement.views import api as datamanagement_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data-management/', datamanagement_api.urls),
    path('', include('sites.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)