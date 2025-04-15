import uuid6
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from iam.models.utils import PermissionChecker
from .orchestration_configuration import OrchestrationConfiguration

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class DataSourceQuerySet(models.QuerySet):
    def visible(self, user: "User"):
        if not user:
            return self.none()
        if user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(workspace__owner=user)
                | Q(
                    workspace__collaborators__user=user,
                    workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "DataSource",
                    ],
                    workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class DataSource(OrchestrationConfiguration, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    workspace = models.ForeignKey(
        "iam.Workspace", related_name="data_sources", on_delete=models.DO_NOTHING
    )
    orchestration_system = models.ForeignKey(
        "OrchestrationSystem", related_name="data_sources", on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    settings = models.JSONField(blank=True, null=True)

    objects = DataSourceQuerySet.as_manager()

    @property
    def status(self):
        return self

    @property
    def schedule(self):
        return self

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="DataSource"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.workspace, resource_type="DataSource"
        )

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from sta.models import Datastream

        data_source_relation_filter = (
            f"data_source__{filter_suffix}" if filter_suffix else "data_source"
        )
        Datastream.objects.filter(**{data_source_relation_filter: filter_arg}).update(
            data_source=None
        )
