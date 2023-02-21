from django.db import models
from django.contrib.auth.models import AbstractUser


class Organization(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, blank=False)
    organizations = models.ManyToManyField(Organization, blank=True, through='Membership')


class Membership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        name = 'no name'
        if self.user:
            if self.user.first_name:
                name = self.user.first_name
        org = 'no org'
        if self.organization:
            if self.organization.name:
                org = self.organization.name
        membership = ' is admin of ' if self.is_admin else ' is member of '
        return name + membership + org
