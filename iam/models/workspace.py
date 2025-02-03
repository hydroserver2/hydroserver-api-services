from django.db import models
from django.conf import settings


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    private = models.BooleanField(default=False)


class WorkspaceTransferConfirmation(models.Model):
    workspace = models.OneToOneField("Workspace", on_delete=models.CASCADE, related_name="transfer_confirmation")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class WorkspaceDeleteConfirmation(models.Model):
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="delete_confirmation")
    initiated = models.DateTimeField()
