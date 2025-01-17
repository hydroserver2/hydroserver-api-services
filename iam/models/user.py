from types import SimpleNamespace
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


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
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(max_length=2000, blank=True, null=True)
    _user_type = models.ForeignKey("UserType", on_delete=models.SET_NULL, blank=True, null=True,
                                   db_column="user_type_id")
    organization = models.OneToOneField("Organization", on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name="user")

    @property
    def permissions(self):
        # TODO: Will be replaced by updated permissions system.
        return SimpleNamespace(enabled=lambda: False)

    @property
    def is_profile_complete(self):
        return all((getattr(self, field) for field in self.REQUIRED_PROFILE_FIELDS))

    @property
    def is_ownership_allowed(self):
        return True

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
    REQUIRED_PROFILE_FIELDS = ["email", "first_name", "last_name", "_user_type"]

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

    def __str__(self):
        return self.name
