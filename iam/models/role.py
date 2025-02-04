import uuid
from django.db import models


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="roles", blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
