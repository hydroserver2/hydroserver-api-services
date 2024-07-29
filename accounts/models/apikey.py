import uuid
import hashlib
import json
from typing import List
from django.db import models
from django.utils.crypto import get_random_string
from django.core.serializers.json import DjangoJSONEncoder
from core.schemas.thing import ThingPatchBody


class PermissionChecker:
    def __init__(self, permissions=None):
        self._permissions = permissions

    def enabled(self):
        return self._permissions is not None

    def is_allowed(self, method: str, model: str):
        return self._permissions is None or any(
            permission.model == model and method in permission.methods for permission in self._permissions
        )

    def check_allowed_fields(self, model: str, fields: List[str]):
        if self.enabled():
            aliased_fields = [getattr(ThingPatchBody, '__fields__', {}).get(field).alias for field in fields]
            for permission in self.get(method='PATCH', model=model):
                if permission.fields and not set(aliased_fields).issubset(set(permission.fields)):
                    return False
        return True

    def get(self, method: str, model: str):
        return [
            permission for permission in self._permissions
            if permission.model == model and method in permission.methods
        ] if self.enabled() else []

    def all(self):
        return self._permissions


class APIKey(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=64, null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    _permissions = models.JSONField(null=True, blank=True, db_column='permissions')
    enabled = models.BooleanField()
    last_used = models.DateTimeField(null=True, blank=True)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    @property
    def permissions(self):
        return self._permissions and json.loads(self._permissions)

    @permissions.setter
    def permissions(self, permissions_dict):
        self._permissions = json.dumps(permissions_dict, cls=DjangoJSONEncoder) if permissions_dict else None

    def generate_token(self, override=False):
        if not self.key or override is True:
            key = get_random_string(length=32)
            self.key = hashlib.sha256(key.encode('utf-8')).hexdigest()
            self.save()
            return key
