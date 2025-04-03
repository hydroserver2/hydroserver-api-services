import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from iam.models.utils import PermissionChecker

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class DataConnectorQuerySet(models.QuerySet):
    def visible(self, user: "User"):
        if user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(workspace__owner=user)
                | Q(
                    workspace__collaborators__user=user,
                    workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "DataConnector",
                    ],
                    workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class DataConnector(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "iam.Workspace", related_name="data_connectors", on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    orchestration_system = models.ForeignKey(
        "OrchestrationSystem", related_name="data_connectors", on_delete=models.DO_NOTHING
    )
    interval = models.PositiveIntegerField(blank=True, null=True)
    interval_units = models.CharField(max_length=255, blank=True, null=True)
    crontab = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    paused = models.BooleanField(default=False)
    last_run_successful = models.BooleanField(blank=True, null=True)
    last_run_message = models.TextField(blank=True, null=True)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)
    settings = models.JSONField(blank=True, null=True)

    objects = DataConnectorQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="DataConnector"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.workspace, resource_type="DataConnector"
        )

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        data_connector_relation_filter = (
            f"data_connector__{filter_suffix}" if filter_suffix else "data_connector"
        )
        LinkedDatastream.objects.filter(
            **{data_connector_relation_filter: filter_arg}
        ).delete()


class LinkedDatastream(models.Model):
    data_connector = models.ForeignKey(
        DataConnector, related_name="linked_datastreams", on_delete=models.DO_NOTHING
    )
    datastream = models.ForeignKey(
        "sta.Datastream", related_name="data_connectors", on_delete=models.DO_NOTHING
    )
    is_data_source = models.BooleanField(default=False)
