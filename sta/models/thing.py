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


class ThingQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(Q(workspace__is_private=False, is_private=False))
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(workspace__is_private=False,
                  is_private=False) |
                Q(workspace__owner=user) |
                Q(workspace__collaborators__user=user,
                  workspace__collaborators__role__permissions__resource_type__in=["*", "Thing"],
                  workspace__collaborators__role__permissions__permission_type__in=["*", "view"])
            )

    def with_location(self):
        return self.prefetch_related("locations").annotate()


class Thing(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, related_name="things", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200)
    description = models.TextField()
    sampling_feature_type = models.CharField(max_length=200)
    sampling_feature_code = models.CharField(max_length=200)
    site_type = models.CharField(max_length=200)
    is_private = models.BooleanField(default=False)
    data_disclaimer = models.TextField(null=True, blank=True)

    objects = ThingQuerySet.as_manager()

    @property
    def location(self):
        if hasattr(self, "_prefetched_objects_cache") and "locations" in self._prefetched_objects_cache:
            locations = self._prefetched_objects_cache["locations"]
            return locations[0] if locations else None
        return self.locations.first()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(user=user, workspace=workspace, resource_type="Thing")

    def get_user_permissions(self, user: Optional["User"]) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(user=user, workspace=self.workspace, resource_type="Thing")

        if not self.workspace.is_private and not self.is_private and "view" not in list(user_permissions):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from sta.models import Datastream, Location, Tag, Photo

        Datastream.delete_contents(filter_arg=filter_arg,
                                   filter_suffix=f"thing__{filter_suffix}" if filter_suffix else "thing")
        Datastream.objects.filter(**{f"thing__{filter_suffix}" if filter_suffix else "thing": filter_arg}).delete()
        Location.objects.filter(**{f"thing__{filter_suffix}" if filter_suffix else "thing": filter_arg}).delete()
        Tag.objects.filter(**{f"thing__{filter_suffix}" if filter_suffix else "thing": filter_arg}).delete()
        Photo.objects.filter(**{f"thing__{filter_suffix}" if filter_suffix else "thing": filter_arg}).delete()
