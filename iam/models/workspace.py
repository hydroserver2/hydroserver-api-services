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
    def get_queryset(self):
        return self.select_related("transfer_confirmation", "delete_confirmation")

    def visible(self, user: Optional["User"]):
        queryset = self.get_queryset()
        if user is None:
            return queryset.filter(is_private=False)
        elif user.account_type == "admin":
            return queryset
        else:
            return queryset.filter(
                Q(is_private=False)
                | Q(owner=user)
                | Q(collaborators__user=user)
                | Q(transfer_confirmation__new_owner=user)
            )

    def associated(self, user: Optional["User"]):
        queryset = self.get_queryset()
        if user is None:
            return queryset.none()
        else:
            return queryset.filter(
                Q(owner=user)
                | Q(collaborators__user=user)
                | Q(transfer_confirmation__new_owner=user)
            )


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    is_private = models.BooleanField(default=False)

    objects = WorkspaceQueryset.as_manager()

    @property
    def link(self):
        return f"{settings.PROXY_BASE_URL}/api/auth/workspaces/{self.id}"

    @property
    def transfer_details(self):
        return getattr(self, "transfer_confirmation", None)

    @property
    def delete_details(self):
        return getattr(self, "delete_confirmation", None)

    @classmethod
    def can_user_create(cls, user: Optional["User"]):
        return user.account_type != "limited"

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        if user and (user == self.owner or user.account_type == "admin"):
            return ["view", "edit", "delete"]
        elif self.is_private is False or self.collaborators.filter(user=user).exists():
            return ["view"]
        elif self.transfer_details and self.transfer_details.new_owner == user:
            return ["view"]
        else:
            return []

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from iam.models import Role, Collaborator
        from sta.models import (
            Thing,
            ObservedProperty,
            ProcessingLevel,
            ResultQualifier,
            Sensor,
            Unit,
        )

        Collaborator.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        Role.delete_contents(
            filter_arg=filter_arg,
            filter_suffix=(
                f"workspace__{filter_suffix}" if filter_suffix else "workspace"
            ),
        )
        Role.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        Thing.delete_contents(
            filter_arg=filter_arg,
            filter_suffix=(
                f"workspace__{filter_suffix}" if filter_suffix else "workspace"
            ),
        )
        Thing.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        ObservedProperty.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        ProcessingLevel.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        ResultQualifier.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        Sensor.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()
        Unit.objects.filter(
            **{
                (
                    f"workspace__{filter_suffix}" if filter_suffix else "workspace"
                ): filter_arg
            }
        ).delete()


class WorkspaceTransferConfirmation(models.Model):
    workspace = models.OneToOneField(
        "Workspace", on_delete=models.CASCADE, related_name="transfer_confirmation"
    )
    new_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    initiated = models.DateTimeField()


class WorkspaceDeleteConfirmation(models.Model):
    workspace = models.OneToOneField(
        "Workspace", on_delete=models.CASCADE, related_name="delete_confirmation"
    )
    initiated = models.DateTimeField()
