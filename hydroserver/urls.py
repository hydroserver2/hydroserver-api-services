from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import accounts.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{settings.ST_PREFIX}/', include('sensorthings.urls')),
    path('', accounts.views.home_view, name='home'),
    path('sites/', include('sites.urls')),
    path('accounts/', include('accounts.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
