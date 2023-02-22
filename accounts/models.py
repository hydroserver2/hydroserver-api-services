from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, blank=False)
    organization = models.CharField(max_length=255, blank=True, null=True)
