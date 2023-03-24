from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from hydroserver.api import api

import accounts.views
import sites.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sensorthings/', include('sensorthings.urls')),
    path('', accounts.views.home_view, name='home'),
    path('sites/', include('sites.urls')),
    path('sites/<str:pk>/', sites.views.site, name="site"),
    path('accounts/', include('accounts.urls')),
    path('api/', api.urls)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
