from django.urls import path
from sensorthings.views import api


urlpatterns = [
    path('v1.1/', api.urls),
]
