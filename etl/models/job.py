import uuid6
from typing import Union, Literal, TYPE_CHECKING
from django.db import models
from django.db.models import Q
from iam.models.utils import PermissionChecker

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace, APIKey

    User = get_user_model()


class JobQuerySet(models.QuerySet):
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
                            "Job",
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
                        "Job",
                    ],
                    workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.none()


class Job(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    name = models.CharField(max_length=255)
    job_type = models.CharField(max_length=255)

    workspace = models.ForeignKey(
        "iam.Workspace", related_name="jobs", on_delete=models.CASCADE
    )

    extractor_type = models.CharField(max_length=255, blank=True, null=True)
    extractor_settings = models.JSONField(default=dict)

    transformer_type = models.CharField(max_length=255, blank=True, null=True)
    transformer_settings = models.JSONField(default=dict)

    loader_type = models.CharField(max_length=255, blank=True, null=True)
    loader_settings = models.JSONField(default=dict)

    objects = JobQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} - {self.id}"

    @property
    def extractor(self):
        return {
            "type": self.extractor_type,
            "settings": self.extractor_settings,
        } if self.extractor_type else None

    @property
    def transformer(self):
        return {
            "type": self.transformer_type,
            "settings": self.transformer_settings,
        } if self.transformer_type else None

    @property
    def loader(self):
        return {
            "type": self.loader_type,
            "settings": self.loader_settings,
        } if self.loader_type else None

    @classmethod
    def can_principal_create(
        cls, principal: Union["User", "APIKey", None], workspace: "Workspace"
    ):
        return cls.check_create_permissions(
            principal=principal, workspace=workspace, resource_type="Job"
        )

    def get_principal_permissions(
        self, principal: Union["User", "APIKey", None]
    ) -> list[Literal["edit", "delete", "view"]]:
        permissions = self.check_object_permissions(
            principal=principal, workspace=self.workspace, resource_type="Job"
        )

        return permissions
