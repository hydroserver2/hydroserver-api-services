import uuid6
import typing
from typing import Literal, Optional, Union
from django.db import models
from django.db.models import Q
from iam.models.utils import PermissionChecker
from .orchestration_configuration import OrchestrationConfiguration

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace, APIKey

    User = get_user_model()


class DataSourceQuerySet(models.QuerySet):
    def visible(self, principal: Union["User", "APIKey"]):
        if not principal:
            return self.none()
        elif hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(workspace__owner=principal)
                    | Q(
                        workspace__collaborators__user=principal,
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
        elif hasattr(principal, "workspace"):
            return self.filter(
                Q(
                    workspace__apikeys=principal,
                    workspace__apikeys__role__permissions__resource_type__in=[
                        "*",
                        "DataSource",
                    ],
                    workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.none()


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
    def can_principal_create(
        cls, principal: Optional[Union["User", "APIKey"]], workspace: "Workspace"
    ):
        return cls.check_create_permissions(
            principal=principal, workspace=workspace, resource_type="DataSource"
        )

    def get_principal_permissions(
        self, principal: Optional[Union["User", "APIKey"]]
    ) -> list[Literal["edit", "delete", "view"]]:
        permissions = self.check_object_permissions(
            principal=principal, workspace=self.workspace, resource_type="DataSource"
        )

        return permissions

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
