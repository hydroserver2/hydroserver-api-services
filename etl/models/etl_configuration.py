import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from iam.models import Workspace
from iam.models.utils import PermissionChecker
from .data_source import DataSource, LinkedDatastream

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class EtlConfigurationQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(Q(etl_system_platform__workspace__isnull=True))
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(etl_system_platform__workspace__isnull=True)
                | Q(etl_system_platform__workspace__owner=user)
                | Q(
                    etl_system_platform__workspace__collaborators__user=user,
                    etl_system_platform__workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "EtlConfiguration",
                    ],
                    etl_system_platform__workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class EtlConfiguration(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etl_system_platform = models.ForeignKey(
        "EtlSystemPlatform",
        related_name="etl_configurations",
        on_delete=models.DO_NOTHING,
    )
    name = models.CharField(max_length=255)
    etl_configuration_model = models.CharField(max_length=255)
    etl_configuration_type = models.CharField(max_length=255)
    etl_configuration_schema = models.JSONField()

    @property
    def data_sources(self):
        return DataSource.objects.filter(
            models.Q(extractor_configuration=self)
            | models.Q(transformer_configuration=self)
            | models.Q(loader_configuration=self)
        ).distinct()

    @property
    def linked_datastreams(self):
        return LinkedDatastream.objects.filter(
            models.Q(extractor_configuration=self)
            | models.Q(transformer_configuration=self)
            | models.Q(loader_configuration=self)
        ).distinct()

    objects = EtlConfigurationQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="EtlConfiguration"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user,
            workspace=self.etl_system_platform.workspace,
            resource_type="EtlConfiguration",
        )

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        etl_configuration_relation_filters = [
            "extractor_configuration",
            "transformer_configuration",
            "loader_configuration",
        ]

        if filter_suffix:
            etl_configuration_relation_filters = [
                f"{relation}__{filter_suffix}"
                for relation in etl_configuration_relation_filters
            ]

        for relation in etl_configuration_relation_filters:
            DataSource.objects.filter(**{relation: filter_arg}).update(
                **{relation: None}
            )
            LinkedDatastream.objects.filter(**{relation: filter_arg}).update(
                **{relation: None}
            )
