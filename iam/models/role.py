import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from .workspace import Workspace
from .utils import PermissionChecker

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class RoleQueryset(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(
                Q(workspace__isnull=True) | Q(workspace__is_private=False)
            )
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(workspace__isnull=True)
                | Q(workspace__is_private=False)
                | Q(workspace__owner=user)
                | Q(
                    workspace__collaborators__user=user,
                    workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "Role",
                    ],
                    workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class Role(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.DO_NOTHING,
        related_name="roles",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    objects = RoleQueryset.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: Workspace):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="Role"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.workspace, resource_type="Role"
        )

        if (not self.workspace or not self.workspace.is_private) and "view" not in list(
            user_permissions
        ):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from iam.models import Permission, Collaborator

        Collaborator.objects.filter(
            **{f"role__{filter_suffix}" if filter_suffix else "role": filter_arg}
        ).delete()
        Permission.objects.filter(
            **{f"role__{filter_suffix}" if filter_suffix else "role": filter_arg}
        ).delete()
