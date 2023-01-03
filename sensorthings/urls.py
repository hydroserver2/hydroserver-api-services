from django.urls import path
from sensorthings.api import api


urlpatterns = [
    path('v1.1/', api.urls),
]
