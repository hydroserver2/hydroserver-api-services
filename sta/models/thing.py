import uuid6
import typing
from typing import Literal, Optional, Union
from django.db import models
from django.db.models import Q
from django.conf import settings
from iam.models import Workspace
from iam.models.utils import PermissionChecker

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace, APIKey

    User = get_user_model()


class ThingQuerySet(models.QuerySet):
    def visible(self, principal: Optional[Union["User", "APIKey"]]):
        if hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(workspace__is_private=False, is_private=False)
                    | Q(workspace__owner=principal)
                    | Q(
                        workspace__collaborators__user=principal,
                        workspace__collaborators__role__permissions__resource_type__in=[
                            "*",
                            "Thing",
                        ],
                        workspace__collaborators__role__permissions__permission_type__in=[
                            "*",
                            "view",
                        ],
                    )
                )
        elif hasattr(principal, "workspace"):
            return self.filter(
                Q(workspace__is_private=False, is_private=False)
                | Q(
                    workspace__apikeys=principal,
                    workspace__apikeys__role__permissions__resource_type__in=[
                        "*",
                        "Thing",
                    ],
                    workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.filter(Q(workspace__is_private=False, is_private=False))

    def with_location(self):
        return self.prefetch_related("locations").annotate()


class Thing(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    workspace = models.ForeignKey(
        Workspace, related_name="things", on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    sampling_feature_type = models.CharField(max_length=200)
    sampling_feature_code = models.CharField(max_length=200)
    site_type = models.CharField(max_length=200)
    is_private = models.BooleanField(default=False)
    data_disclaimer = models.TextField(null=True, blank=True)

    objects = ThingQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} - {self.id}"

    @property
    def location(self):
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "locations" in self._prefetched_objects_cache
        ):
            locations = self._prefetched_objects_cache["locations"]
            return locations[0] if locations else None
        return self.locations.first()

    @classmethod
    def can_principal_create(
        cls, principal: Optional[Union["User", "APIKey"]], workspace: "Workspace"
    ):
        return cls.check_create_permissions(
            principal=principal, workspace=workspace, resource_type="Thing"
        )

    def get_principal_permissions(
        self, principal: Optional[Union["User", "APIKey"]]
    ) -> list[Literal["edit", "delete", "view"]]:
        permissions = self.check_object_permissions(
            principal=principal, workspace=self.workspace, resource_type="Thing"
        )

        if (
            not self.workspace.is_private
            and not self.is_private
            and "view" not in list(permissions)
        ):
            permissions = list(permissions) + ["view"]

        return permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from sta.models import Datastream, Location, ThingTag, ThingFileAttachment

        thing_relation_filter = f"thing__{filter_suffix}" if filter_suffix else "thing"

        Datastream.delete_contents(
            filter_arg=filter_arg, filter_suffix=thing_relation_filter
        )
        Datastream.objects.filter(**{thing_relation_filter: filter_arg}).delete()

        Location.objects.filter(**{thing_relation_filter: filter_arg}).delete()
        ThingTag.objects.filter(**{thing_relation_filter: filter_arg}).delete()
        ThingFileAttachment.objects.filter(
            **{thing_relation_filter: filter_arg}
        ).delete()


class ThingTagQuerySet(models.QuerySet):
    def visible(self, principal: Optional[Union["User", "APIKey"]]):
        if hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(thing__workspace__is_private=False, thing__is_private=False)
                    | Q(thing__workspace__owner=principal)
                    | Q(
                        thing__workspace__collaborators__user=principal,
                        thing__workspace__collaborators__role__permissions__resource_type__in=[
                            "*",
                            "Thing",
                        ],
                        thing__workspace__collaborators__role__permissions__permission_type__in=[
                            "*",
                            "view",
                        ],
                    )
                )
        elif hasattr(principal, "workspace"):
            return self.filter(
                Q(thing__workspace__is_private=False, thing__is_private=False)
                | Q(
                    thing__workspace__apikeys=principal,
                    thing__workspace__apikeys__role__permissions__resource_type__in=[
                        "*",
                        "Thing",
                    ],
                    thing__workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.filter(
                Q(thing__workspace__is_private=False, thing__is_private=False)
            )


class ThingTag(models.Model, PermissionChecker):
    thing = models.ForeignKey(
        Thing, related_name="thing_tags", on_delete=models.DO_NOTHING
    )
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value} - {self.id}"

    objects = ThingTagQuerySet.as_manager()


def thing_file_attachment_storage_path(instance, filename):
    return f"things/{instance.thing.id}/{filename}"


class ThingFileAttachment(models.Model, PermissionChecker):
    thing = models.ForeignKey(
        Thing, related_name="thing_file_attachments", on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    file_attachment = models.FileField(upload_to=thing_file_attachment_storage_path)
    file_attachment_type = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.id}"

    @property
    def link(self):
        storage = self.file_attachment.storage

        try:
            file_attachment_link = storage.url(self.file_attachment.name, expire=3600)
        except TypeError:
            file_attachment_link = storage.url(self.file_attachment.name)

        if settings.DEPLOYMENT_BACKEND == "local":
            file_attachment_link = settings.PROXY_BASE_URL + file_attachment_link

        return file_attachment_link

    class Meta:
        unique_together = ("thing", "name")


class SamplingFeatureType(models.Model):
    name = models.CharField(max_length=200, unique=True)


class SiteType(models.Model):
    name = models.CharField(max_length=200, unique=True)


class FileAttachmentType(models.Model):
    name = models.CharField(max_length=200, unique=True)
