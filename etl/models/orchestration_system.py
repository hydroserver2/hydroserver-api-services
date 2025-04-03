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


class OrchestrationSystemQuerySet(models.QuerySet):
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
                        "EtlSystem",
                    ],
                    workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class OrchestrationSystem(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="OrchestrationSystem"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.workspace, resource_type="OrchestrationSystem"
        )

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from etl.models import DataConnector

        orchestration_system_relation_filter = (
            f"orchestration_system__{filter_suffix}" if filter_suffix else "orchestration_system"
        )

        DataConnector.delete_contents(
            filter_arg=filter_arg, filter_suffix=orchestration_system_relation_filter
        )
        DataConnector.objects.filter(**{orchestration_system_relation_filter: filter_arg}).delete()
