import uuid
import typing
from typing import Literal, Optional
from django.db import models
from django.db.models import Q
from iam.models import Workspace
from iam.models.utils import PermissionChecker
from .thing import Thing
from .sensor import Sensor
from .unit import Unit
from .processing_level import ProcessingLevel
from .observed_property import ObservedProperty

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class DatastreamQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(
                Q(
                    thing__workspace__is_private=False,
                    thing__is_private=False,
                    is_private=False,
                )
            )
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(
                    thing__workspace__is_private=False,
                    thing__is_private=False,
                    is_private=False,
                )
                | Q(thing__workspace__owner=user)
                | Q(
                    thing__workspace__collaborators__user=user,
                    thing__workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "Datastream",
                    ],
                    thing__workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class Datastream(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    thing = models.ForeignKey(
        Thing, on_delete=models.DO_NOTHING, related_name="datastreams"
    )
    sensor = models.ForeignKey(
        Sensor, on_delete=models.DO_NOTHING, related_name="datastreams"
    )
    observed_property = models.ForeignKey(
        ObservedProperty, on_delete=models.DO_NOTHING, related_name="datastreams"
    )
    processing_level = models.ForeignKey(
        ProcessingLevel, on_delete=models.DO_NOTHING, related_name="datastreams"
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.DO_NOTHING, related_name="datastreams"
    )
    observation_type = models.CharField(max_length=255)
    result_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True, blank=True)
    observed_area = models.CharField(max_length=255, null=True, blank=True)  # Unused
    sampled_medium = models.CharField(max_length=255)
    value_count = models.IntegerField(null=True, blank=True)
    no_data_value = models.FloatField()
    intended_time_spacing = models.FloatField(null=True, blank=True)
    intended_time_spacing_unit = models.CharField(max_length=255, null=True, blank=True)
    aggregation_statistic = models.CharField(max_length=255)
    time_aggregation_interval = models.FloatField()
    time_aggregation_interval_unit = models.CharField(max_length=255)
    phenomenon_begin_time = models.DateTimeField(null=True, blank=True)
    phenomenon_end_time = models.DateTimeField(null=True, blank=True)
    result_end_time = models.DateTimeField(null=True, blank=True)  # Unused
    result_begin_time = models.DateTimeField(null=True, blank=True)  # Unused
    is_private = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    data_source = models.ForeignKey(
        "etl.DataSource",
        related_name="datastreams",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    data_archives = models.ManyToManyField(
        "etl.DataArchive", related_name="datastreams"
    )

    objects = DatastreamQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="Datastream"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user, workspace=self.thing.workspace, resource_type="Datastream"
        )

        if (
            not self.thing.workspace.is_private
            and not self.thing.is_private
            and not self.is_private
            and "view" not in list(user_permissions)
        ):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions

    def delete(self, *args, **kwargs):
        self.delete_contents(filter_arg=self, filter_suffix="")
        super().delete(*args, **kwargs)

    @staticmethod
    def delete_contents(filter_arg: models.Model, filter_suffix: Optional[str]):
        from sta.models import Observation, Datastream

        datastream_relation_filter = (
            f"datastream__{filter_suffix}" if filter_suffix else "datastream"
        )

        Observation.objects.filter(**{datastream_relation_filter: filter_arg}).delete()

        Datastream.data_archives.through.objects.filter(
            **{datastream_relation_filter: filter_arg}
        ).delete()


class DatastreamAggregation(models.Model):
    name = models.CharField(max_length=255, unique=True)


class DatastreamStatus(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Datastream statuses"


class SampledMedium(models.Model):
    name = models.CharField(max_length=255, unique=True)
