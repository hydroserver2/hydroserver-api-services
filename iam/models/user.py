from types import SimpleNamespace
from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().select_related('_user_type', 'organization', 'organization___organization_type')

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
        user_type, _ = UserType.objects.get_or_create(
            name="Admin",
            defaults={"public": False}
        )

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("_user_type", user_type)

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
    _user_type = models.ForeignKey("UserType", on_delete=models.PROTECT, db_column="user_type_id")
    organization = models.OneToOneField("Organization", on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name="user")
    is_ownership_allowed = models.BooleanField(default=False)

    @property
    def permissions(self):
        # TODO: Will be replaced by updated permissions system.
        return SimpleNamespace(enabled=lambda: False)

    @property
    def account_type(self):
        if self.is_superuser:
            return "admin"
        elif self.is_ownership_allowed:
            return "standard"
        else:
            return "limited"

    @property
    def user_type(self):
        return self._user_type.name

    @user_type.setter
    def user_type(self, value):
        try:
            self._user_type = None if value is None else UserType.objects.get(name=value)
        except UserType.DoesNotExist:
            raise ValueError(f"'{value}' is not an allowed user type.")

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
