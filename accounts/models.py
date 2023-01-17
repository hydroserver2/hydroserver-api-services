from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    affiliation_id = models.IntegerField(null=True)  # Temporarily nullable
    email = models.EmailField(max_length=254, unique=True, blank=False)
    # organization_code = models.CharField(max_length=50, blank=True, null=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)

    # def owns_site(self, registration):
    #     return registration.django_user == self
    #
    # def can_administer_site(self, registration):
    #     return self.is_staff or registration.django_user == self
