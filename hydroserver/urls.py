from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from hydroserver.views import index, csrf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/csrf/', csrf, name='csrf'),
    path('api/auth/', include('allauth.headless.urls')),
    path('api/account/', include('iam.urls')),
    path('api/data/', include('core.urls')),
    path('api/sensorthings/', include('stapi.urls')),
    path('', index)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
