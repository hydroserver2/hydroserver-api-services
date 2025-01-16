from typing import Optional, Any
from ninja.security.apikey import APIKeyCookie
from ninja.errors import HttpError
from django.http import HttpRequest
from django.conf import settings


class SessionAuth(APIKeyCookie):
    param_name: str = settings.SESSION_COOKIE_NAME

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if key and request.user.is_authenticated:
            request.authenticated_user = request.user
            return request.user
        elif key:
            raise HttpError(401, 'Invalid or missing session cookie')
