import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from iam.models import Workspace
from iam.models.utils import PermissionChecker
from .datastream import Datastream

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class ObservationQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(Q(datastream__thing__workspace__is_private=False, datastream__thing__is_private=False,
                                 datastream__is_private=False))
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(datastream__thing__workspace__is_private=False,
                  datastream__thing__is_private=False,
                  datastream__is_private=False) |
                Q(datastream__thing__workspace__owner=user) |
                Q(datastream__thing__workspace__collaborators__user=user,
                  datastream__thing__workspace__collaborators__role__permissions__resource_type__in=[
                      "*", "Observation"
                  ],
                  datastream__thing__workspace__collaborators__role__permissions__permission_type__in=["*", "view"])
            )

    def removable(self, user: Optional["User"]):
        if user is None:
            return self.none()
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(datastream__thing__workspace__owner=user) |
                Q(datastream__thing__workspace__collaborators__user=user,
                  datastream__thing__workspace__collaborators__role__permissions__resource_type__in=[
                      "*", "Observation"
                  ],
                  datastream__thing__workspace__collaborators__role__permissions__permission_type__in=["*", "delete"])
            )


class Observation(models.Model, PermissionChecker):
    pk = models.CompositePrimaryKey("datastream_id", "phenomenon_time", "id")
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    datastream = models.ForeignKey(Datastream, on_delete=models.DO_NOTHING)
    phenomenon_time = models.DateTimeField()
    result = models.FloatField()
    result_time = models.DateTimeField(null=True, blank=True)
    quality_code = models.CharField(max_length=255, null=True, blank=True)

    objects = ObservationQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(user=user, workspace=workspace, resource_type="Observation")

    def get_user_permissions(self, user: Optional["User"]) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(user=user, workspace=self.datastream.thing.workspace,
                                                         resource_type="Observation")

        if (not self.datastream.thing.workspace.is_private and not self.datastream.thing.is_private
                and not self.datastream.is_private and "view" not in list(user_permissions)):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["datastream_id", "phenomenon_time"], name="unique_datastream_timestamps")
        ]
