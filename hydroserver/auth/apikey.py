import datetime
import hashlib
import json
from ninja.security import APIKeyHeader, APIKeyQuery, APIKeyCookie
from ninja.errors import HttpError
from accounts.models import APIKey, PermissionChecker
from accounts.endpoints.apikey.schemas import APIKeyPermissions
from django.utils import timezone
from django.db.models import Q


class APIKeyAuthCheck:
    def authenticate(self, request, key, *args, **kwargs):
        if not key:
            return None

        try:
            api_key = APIKey.objects.select_related('person').filter(
                Q(expires__isnull=True) | Q(expires__gt=timezone.now()),
                key=hashlib.sha256(key.encode('utf-8')).hexdigest()
            ).get()
        except (APIKey.DoesNotExist, AttributeError, UnicodeDecodeError, ValueError):
            raise HttpError(401, 'API key invalid or expired')

        user = api_key.person

        if user and user.is_active and api_key.enabled and \
                (not api_key.expires or api_key.expires > datetime.datetime.now()):
            request.authenticated_user = user
            request.authenticated_user.permissions = PermissionChecker([
                APIKeyPermissions(**permission) for permission in json.loads(api_key.permissions)
            ])
            return user


class APIKeyQueryAuth(APIKeyAuthCheck, APIKeyQuery):
    pass


class APIKeyHeaderAuth(APIKeyAuthCheck, APIKeyHeader):
    pass


class APIKeyCookieAuth(APIKeyAuthCheck, APIKeyCookie):
    pass
