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


class EtlSystemPlatformQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(Q(workspace__isnull=True))
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(workspace__isnull=True)
                | Q(workspace__owner=user)
                | Q(
                    workspace__collaborators__user=user,
                    workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "EtlSystemPlatform",
                    ],
                    workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class EtlSystemPlatform(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        related_name="etl_system_platforms",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    interval_schedule_supported = models.BooleanField(default=False)
    crontab_schedule_supported = models.BooleanField(default=False)

    objects = EtlSystemPlatformQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="EtlSystemPlatform"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.workspace, resource_type="EtlSystemPlatform"
        )

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from etl.models import EtlSystem, EtlConfiguration

        etl_system_platform_relation_filter = (
            f"etl_system_platform__{filter_suffix}"
            if filter_suffix
            else "etl_system_platform"
        )

        EtlSystem.delete_contents(
            filter_arg=filter_arg, filter_suffix=etl_system_platform_relation_filter
        )
        EtlSystem.objects.filter(
            **{etl_system_platform_relation_filter: filter_arg}
        ).delete()
        EtlConfiguration.objects.filter(
            **{etl_system_platform_relation_filter: filter_arg}
        ).delete()
