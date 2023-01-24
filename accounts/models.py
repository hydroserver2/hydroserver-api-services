from django.db import models
from django.contrib.auth.models import AbstractUser


class Organization(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, blank=False)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)



