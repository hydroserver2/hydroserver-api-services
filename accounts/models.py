import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        uid = f'{uuid.uuid4()}@hydroserver-temp.org'

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


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    unverified_email = models.EmailField(blank=True, null=True)
    orcid = models.CharField(max_length=255, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    link = models.URLField(max_length=2000, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


class PasswordReset(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.timestamp <= timedelta(days=1)
