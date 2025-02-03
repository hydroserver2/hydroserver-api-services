from django.db import models


class Role(models.Model):
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="roles", blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
