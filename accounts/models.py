import uuid
import hashlib
from typing import List
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
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


class PersonManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):

        if email is not None:
            unverified_email = self.normalize_email(email)
        else:
            unverified_email = None

        if extra_fields.get('is_superuser') is True:
            user = self.model(
                username=email,
                email=email,
                is_verified=True,
                **extra_fields
            )
        else:
            uid = f'{uuid.uuid4()}@hydroserver-temp.org'
            user = self.model(
                username=uid,
                email=uid,
                unverified_email=unverified_email,
                **extra_fields
            )

        if password is not None:
            user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Organization(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255)
    link = models.URLField(max_length=2000, blank=True, null=True)


class Person(AbstractUser):
    email = models.EmailField(unique=True)
    unverified_email = models.EmailField(blank=True, null=True)
    orcid = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    link = models.URLField(max_length=2000, blank=True, null=True)
    organization = models.OneToOneField(Organization, related_name='person', on_delete=models.SET_NULL,  
                                        db_column='organizationId', blank=True, null=True)
    hydroshare_token = models.JSONField(blank=True, null=True)

    objects = PersonManager()

    @property
    def permissions(self):
        return getattr(self, '_permissions', PermissionChecker())

    @permissions.setter
    def permissions(self, permissions: PermissionChecker):
        self._permissions = permissions

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


class PasswordReset(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    user = models.OneToOneField('Person', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.timestamp <= timedelta(days=1)


class APIKey(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=64, null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    permissions = models.JSONField(null=True, blank=True)
    enabled = models.BooleanField()
    last_used = models.DateTimeField(null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def generate_token(self, override=False):
        if not self.key or override is True:
            key = get_random_string(length=32)
            self.key = hashlib.sha256(key.encode('utf-8')).hexdigest()
            self.save()
            return key
