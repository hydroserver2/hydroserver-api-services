import io
import uuid6
import typing
from typing import Literal, Optional
from django.db import models, connection
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
            return self.filter(
                Q(
                    datastream__thing__workspace__is_private=False,
                    datastream__thing__is_private=False,
                    datastream__is_private=False,
                )
            )
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(
                    datastream__thing__workspace__is_private=False,
                    datastream__thing__is_private=False,
                    datastream__is_private=False,
                )
                | Q(datastream__thing__workspace__owner=user)
                | Q(
                    datastream__thing__workspace__collaborators__user=user,
                    datastream__thing__workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "Observation",
                    ],
                    datastream__thing__workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )

    def removable(self, user: Optional["User"]):
        if user is None:
            return self.none()
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(datastream__thing__workspace__owner=user)
                | Q(
                    datastream__thing__workspace__collaborators__user=user,
                    datastream__thing__workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "Observation",
                    ],
                    datastream__thing__workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "delete",
                    ],
                )
            )

    def bulk_copy(self, observations, batch_size=100_000):
        db_table_sql = connection.ops.quote_name(self.model._meta.db_table)  # noqa
        db_fields = [
            field.column for field in self.model._meta.fields if not field.primary_key
        ]  # noqa
        db_fields_sql = ", ".join(
            connection.ops.quote_name(field) for field in db_fields
        )

        def escape_pg_copy(value):
            if value is None:
                return r"\N"
            if isinstance(value, str):
                return (
                    value.replace("\\", "\\\\")
                    .replace("\t", "\\t")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                )
            return str(value)

        with connection.cursor() as cursor:
            with cursor.copy(
                f"COPY {db_table_sql} ({db_fields_sql}) FROM STDIN"
            ) as copy:
                buffer = io.StringIO()
                for i in range(0, len(observations), batch_size):
                    batch = observations[i : i + batch_size]
                    buffer.write(
                        "\n".join(
                            "\t".join(
                                escape_pg_copy(getattr(obs, field, None))
                                for field in db_fields
                            )
                            for obs in batch
                        )
                        + "\n"
                    )
                    buffer.seek(0)
                    copy.write(buffer.read())
                    buffer.truncate(0)
                    buffer.seek(0)

        return observations


class Observation(models.Model, PermissionChecker):
    pk = models.CompositePrimaryKey("datastream_id", "phenomenon_time")
    id = models.UUIDField(default=uuid6.uuid7, editable=False)
    datastream = models.ForeignKey(Datastream, on_delete=models.DO_NOTHING)
    phenomenon_time = models.DateTimeField()
    result = models.FloatField()
    result_time = models.DateTimeField(null=True, blank=True)
    quality_code = models.CharField(max_length=255, null=True, blank=True)

    objects = ObservationQuerySet.as_manager()

    @classmethod
    def can_user_create(cls, user: Optional["User"], workspace: "Workspace"):
        return cls.check_create_permissions(
            user=user, workspace=workspace, resource_type="Observation"
        )

    def get_user_permissions(
        self, user: Optional["User"]
    ) -> list[Literal["edit", "delete", "view"]]:
        user_permissions = self.check_object_permissions(
            user=user,
            workspace=self.datastream.thing.workspace,
            resource_type="Observation",
        )

        if (
            not self.datastream.thing.workspace.is_private
            and not self.datastream.thing.is_private
            and not self.datastream.is_private
            and "view" not in list(user_permissions)
        ):
            user_permissions = list(user_permissions) + ["view"]

        return user_permissions

    class Meta:
        indexes = [models.Index(fields=["id"])]
