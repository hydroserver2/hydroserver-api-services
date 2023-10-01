from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
# from sites.endpoints import endpoints
from hydroserver.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('endpoints/', endpoints.urls),
    path('endpoints/data/', include('core.urls')),
    path('endpoints/account/', include('accounts.urls')),
    path('endpoints/sensorthings/', include('stapi.urls')),
    path('', index)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
