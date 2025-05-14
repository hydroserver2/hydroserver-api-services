import uuid6
import typing
from typing import Literal, Optional, Union
from django.db import models
from django.db.models import Q
from iam.models import Workspace
from iam.models.utils import PermissionChecker

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace, APIKey

    User = get_user_model()


class OrchestrationSystemQuerySet(models.QuerySet):
    def visible(self, principal: Optional[Union["User", "APIKey"]]):
        if not principal:
            return self.filter(Q(workspace__isnull=True))
        elif hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(workspace__isnull=True)
                    | Q(workspace__owner=principal)
                    | Q(
                        workspace__collaborators__user=principal,
                        workspace__collaborators__role__permissions__resource_type__in=[
                            "*",
                            "OrchestrationSystem",
                        ],
                        workspace__collaborators__role__permissions__permission_type__in=[
                            "*",
                            "view",
                        ],
                    )
                )
        elif hasattr(principal, "workspace"):
            return self.filter(
                Q(workspace__isnull=True)
                | Q(
                    workspace__apikeys=principal,
                    workspace__apikeys__role__permissions__resource_type__in=[
                        "*",
                        "OrchestrationSystem",
                    ],
                    workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.filter(Q(workspace__isnull=True))


class OrchestrationSystem(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        related_name="orchestration_systems",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    orchestration_system_type = models.CharField(max_length=255)

    objects = OrchestrationSystemQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} - {self.id}"

    @classmethod
    def can_principal_create(
        cls, principal: Optional[Union["User", "APIKey"]], workspace: "Workspace"
    ):
        return cls.check_create_permissions(
            principal=principal,
            workspace=workspace,
            resource_type="OrchestrationSystem",
        )

    def get_principal_permissions(
        self, principal: Optional[Union["User", "APIKey"]]
    ) -> list[Literal["edit", "delete", "view"]]:
        permissions = self.check_object_permissions(
            principal=principal,
            workspace=self.workspace,
            resource_type="OrchestrationSystem",
        )

        return permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from etl.models import DataSource, DataArchive

        orchestration_system_relation_filter = (
            f"orchestration_system__{filter_suffix}"
            if filter_suffix
            else "orchestration_system"
        )

        DataSource.delete_contents(
            filter_arg=filter_arg, filter_suffix=orchestration_system_relation_filter
        )
        DataSource.objects.filter(
            **{orchestration_system_relation_filter: filter_arg}
        ).delete()
        DataArchive.delete_contents(
            filter_arg=filter_arg, filter_suffix=orchestration_system_relation_filter
        )
        DataArchive.objects.filter(
            **{orchestration_system_relation_filter: filter_arg}
        ).delete()
