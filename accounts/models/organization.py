import uuid
from django.db import models


class Organization(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255)
    link = models.URLField(max_length=2000, blank=True, null=True)
