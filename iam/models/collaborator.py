import uuid
from typing import Literal
from django.db import models
from django.db.models import Q
from django.conf import settings
from .workspace import Workspace
from .utils import PermissionChecker


class CollaboratorQueryset(models.QuerySet):
    def visible(self, user: settings.AUTH_USER_MODEL):
        return self.filter(
            Q(workspace__isnull=True) |
            Q(workspace__private=False) |
            Q(workspace__owner=user) |
            Q(workspace__collaborators__user=user,
              workspace__collaborators__role__permissions__resource_type__in=["*", "Collaborator"],
              workspace__collaborators__role__permissions__permission_type__in=["*", "view"])
        )


class Collaborator(models.Model, PermissionChecker):
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="collaborators")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_roles")
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="collaborator_assignments")

    objects = CollaboratorQueryset.as_manager()

    @classmethod
    def can_user_create(cls, user: settings.AUTH_USER_MODEL, workspace: Workspace):
        return cls.check_create_permissions(user=user, workspace=workspace, resource_type="Collaborator")

    def get_user_permissions(self, user: settings.AUTH_USER_MODEL) -> list[Literal["edit", "delete", "view"]]:
        return self.check_object_permissions(user=user, workspace=self.workspace, resource_type="Collaborator")

    class Meta:
        unique_together = ("user", "workspace")
