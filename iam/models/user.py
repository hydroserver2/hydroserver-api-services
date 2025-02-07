from types import SimpleNamespace
from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().select_related('organization')

    def create_user(self, email, password, **extra_fields):
        if email is None:
            raise ValueError("Users must have an email address")

        normalized_email = self.normalize_email(email)

        user = self.model(
            username=normalized_email,
            email=normalized_email,
            **extra_fields
        )
        user.is_ownership_allowed = user.is_superuser or settings.ACCOUNT_OWNERSHIP_ENABLED
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "Admin")

        user = self.create_user(email, password, **extra_fields)

        EmailAddress.objects.create(
            user=user,
            email=email,
            verified=True,
            primary=True
        )

        return user


class User(AbstractUser):
    email = models.EmailField(unique=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(max_length=2000, blank=True, null=True)
    user_type = models.CharField(max_length=255)
    organization = models.OneToOneField("Organization", on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name="user")
    is_ownership_allowed = models.BooleanField(default=False)

    @property
    def permissions(self):
        # TODO: Will be replaced by updated permissions system.
        return SimpleNamespace(enabled=lambda: False)

    @property
    def name(self):
        return self.__str__

    @property
    def organization_name(self):
        return self.organization.name if self.organization else None

    @property
    def account_type(self):
        if self.is_superuser:
            return "admin"
        elif self.is_ownership_allowed:
            return "standard"
        else:
            return "limited"

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        if self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.name
