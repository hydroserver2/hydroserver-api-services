from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from ninja.security import APIKeyHeader
from iam.models import APIKey


class APIKeyAuth(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        now = timezone.now()
        for api_key in APIKey.objects.filter(is_active=True).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ):
            if check_password(key, api_key.hashed_key):
                api_key.last_used_at = now
                api_key.save(update_fields=["last_used"])
                request.principal = api_key

                return api_key
