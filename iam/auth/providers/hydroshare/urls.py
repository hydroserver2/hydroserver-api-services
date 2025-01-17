from django.urls import path

from allauth.socialaccount.providers.google import views
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import HydroShareProvider


urlpatterns = default_urlpatterns(HydroShareProvider)

urlpatterns += [
    path(
        "hydroshare/login/token/",
        views.login_by_token,
        name="hydroshare_login_by_token",
    ),
]
