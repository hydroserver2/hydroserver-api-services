from django.urls import path
from sensorthings.api import api


urlpatterns = [
    path('', api.urls),
]
