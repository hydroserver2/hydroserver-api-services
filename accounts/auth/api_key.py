import hashlib
from ninja.security import APIKeyHeader, APIKeyQuery, APIKeyCookie
from ninja.errors import HttpError
from accounts.models import APIKey
from django.utils import timezone
from django.db.models import Q


class APIKeyAuthCheck(APIKeyHeader):
    def authenticate(self, request, key, *args, **kwargs):
        try:
            api_key = APIKey.objects.select_related('person').filter(
                Q(expires__isnull=True) | Q(expires__gt=timezone.now()),
                key=hashlib.sha256(key.encode('utf-8')).hexdigest()
            ).get()
        except (APIKey.DoesNotExist, UnicodeDecodeError, ValueError):
            raise HttpError(401, 'API key invalid or expired')

        user = api_key.person

        if user and user.is_active:
            request.authenticated_user = user
            request.permissions = api_key.permissions
            return user


# class APIKeyQueryAuth(APIKeyAuthCheck, APIKeyQuery):
#     pass
#
#
# class APIAPIKeyHeaderAuth(APIKeyAuthCheck, APIKeyHeader):
#     pass
#
#
# class APIKeyCookieAuth(APIKeyAuthCheck, APIKeyCookie):
#     pass
