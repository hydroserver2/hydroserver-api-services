import uuid
from typing import Literal
from django.db import models
from django.db.models import Q
from django.conf import settings
from .workspace import Workspace
from .utils import PermissionChecker


class RoleQueryset(models.QuerySet):
    def visible(self, user: settings.AUTH_USER_MODEL):
        return self.filter(
            Q(workspace__isnull=True) |
            Q(workspace__private=False) |
            Q(workspace__owner=user) |
            Q(workspace__collaborators__user=user,
              workspace__collaborators__role__permissions__resource_type__in=["*", "Role"],
              workspace__collaborators__role__permissions__permission_type__in=["*", "view"])
        )


class Role(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="roles", blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    objects = RoleQueryset.as_manager()

    @classmethod
    def can_user_create(cls, user: settings.AUTH_USER_MODEL, workspace: Workspace):
        return cls.check_create_permissions(user=user, workspace=workspace, resource_type="Role")

    def get_user_permissions(self, user: settings.AUTH_USER_MODEL) -> list[Literal["edit", "delete", "view"]]:
        return self.check_object_permissions(user=user, workspace=self.workspace, resource_type="Role")
