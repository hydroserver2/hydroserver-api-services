from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from hydroserver.api import api
from hydroserver.views import index

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('sensorthings/', include('sensorthings.urls')),
    path('api/', api.urls)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
