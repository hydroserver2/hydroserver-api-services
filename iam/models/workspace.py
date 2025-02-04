import uuid
from typing import Literal
from django.db import models
from django.db.models import Q
from django.conf import settings


class WorkspaceQueryset(models.QuerySet):
    def visible(self, user: settings.AUTH_USER_MODEL):
        return self.filter(Q(private=False) | Q(owner=user) | Q(collaborators__user=user))

    def associated(self, user: settings.AUTH_USER_MODEL):
        return self.filter(Q(owner=user) | Q(collaborators__user=user))


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    private = models.BooleanField(default=False)

    objects = WorkspaceQueryset.as_manager()

    @classmethod
    def can_user_create(cls, user: settings.AUTH_USER_MODEL):
        return user.account_type != "limited"

    def get_user_permissions(self, user: settings.AUTH_USER_MODEL) -> list[Literal["edit", "delete", "view"]]:
        if user == self.owner:
            return ["view", "edit", "delete"]
        elif self.private is False or self.collaborators.filter(user=user).exists():
            return ["view"]
        else:
            return []


class WorkspaceTransferConfirmation(models.Model):
    workspace = models.OneToOneField("Workspace", on_delete=models.CASCADE, related_name="transfer_confirmation")
    new_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    initiated = models.DateTimeField()


class WorkspaceDeleteConfirmation(models.Model):
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="delete_confirmation")
    initiated = models.DateTimeField()
