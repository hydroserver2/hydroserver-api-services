from django.db import models
from django.conf import settings


class Collaborator(models.Model):
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="collaborators")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_roles")
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="collaborator_assignments")

    class Meta:
        unique_together = ("user", "workspace")
