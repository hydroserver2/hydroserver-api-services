import uuid6
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


class SensorQuerySet(models.QuerySet):
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
                        "Sensor",
                    ],
                    workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class Sensor(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        related_name="sensors",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    sensor_model = models.CharField(max_length=255, null=True, blank=True)
    sensor_model_link = models.CharField(max_length=500, null=True, blank=True)
    method_type = models.CharField(max_length=100)
    method_link = models.CharField(max_length=500, blank=True, null=True)
    method_code = models.CharField(max_length=50, blank=True, null=True)

    objects = SensorQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="Sensor"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.workspace, resource_type="Sensor"
        )

        if (not self.workspace or not self.workspace.is_private) and "view" not in list(
            user_permissions
        ):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions


class SensorEncodingType(models.Model):
    name = models.CharField(max_length=255, unique=True)


class MethodType(models.Model):
    name = models.CharField(max_length=255, unique=True)
