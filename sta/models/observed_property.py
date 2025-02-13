import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from iam.models import Workspace
from iam.models.utils import PermissionChecker

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class ObservedPropertyQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(
                Q(workspace__isnull=True) |
                Q(workspace__is_private=False)
            )
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(workspace__isnull=True) |
                Q(workspace__is_private=False) |
                Q(workspace__owner=user) |
                Q(workspace__collaborators__user=user,
                  workspace__collaborators__role__permissions__resource_type__in=["*", "ObservedProperty"],
                  workspace__collaborators__role__permissions__permission_type__in=["*", "view"])
            )


class ObservedProperty(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, related_name="observed_properties", on_delete=models.DO_NOTHING,
                                  blank=True, null=True)
    name = models.CharField(max_length=255)
    definition = models.TextField()
    description = models.TextField()
    observed_property_type = models.CharField(max_length=500)
    code = models.CharField(max_length=500)

    objects = ObservedPropertyQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(user=user, workspace=workspace, resource_type="ObservedProperty")

    def get_user_permissions(self, user: Optional["User"]) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(user=user, workspace=self.workspace,
                                                         resource_type="ObservedProperty")

        if (not self.workspace or not self.workspace.is_private) and "view" not in list(user_permissions):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions
