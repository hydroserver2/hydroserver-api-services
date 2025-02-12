from typing import Optional, Any, Tuple
from ninja.security.apikey import APIKeyCookie
from ninja.errors import HttpError
from ninja.utils import check_csrf
from django.http import HttpRequest
from django.conf import settings


class SessionAuth(APIKeyCookie):
    param_name: str = settings.SESSION_COOKIE_NAME

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        csrf_passed = check_csrf(request) if self.csrf else True
        if key and csrf_passed and request.user.is_authenticated:
            request.authenticated_user = request.user
            return request.user
        elif key and csrf_passed:
            raise HttpError(401, 'Invalid or missing session cookie')
        elif key and csrf_passed is False:
            raise HttpError(403, "CSRF check Failed")

    def _get_key(self, request: HttpRequest) -> tuple[Any, bool]:
        return request.COOKIES.get(self.param_name)
