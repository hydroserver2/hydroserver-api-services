import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from django.conf import settings

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class WorkspaceQueryset(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(private=False)
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(private=False) |
                Q(owner=user) |
                Q(collaborators__user=user) |
                Q(transfer_confirmation__new_owner=user)
            )

    def associated(self, user: Optional["User"]):
        if user is None:
            return self.none()
        else:
            return self.filter(Q(owner=user) | Q(collaborators__user=user) | Q(transfer_confirmation__new_owner=user))


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    private = models.BooleanField(default=False)

    objects = WorkspaceQueryset.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"]):
        return user.account_type != "limited"

    def get_user_permissions(self, user: Optional["User"]) -> list[Literal["edit", "delete", "view"]]:
        if user == self.owner or user.account_type == "admin":
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
