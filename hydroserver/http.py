from typing import Optional
from django.http import HttpRequest
from django.conf import settings


class HydroServerHttpRequest(HttpRequest):
    authenticated_user: Optional[settings.AUTH_USER_MODEL]
