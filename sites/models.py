from django.db.models import DecimalField
from django.db import models
import uuid


class Site(models.Model):
    name = models.CharField(max_length=200)
    latitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    elevation = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.name
