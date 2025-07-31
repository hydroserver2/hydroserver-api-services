import io
import uuid6
import typing
import operator
from typing import Literal, Optional, Union
from django.db import models, connection
from django.db.models import Q
from iam.models import Workspace, Permission
from iam.models.utils import PermissionChecker
from .datastream import Datastream
from .result_qualifier import ResultQualifier

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace, APIKey

    User = get_user_model()


class ObservationQuerySet(models.QuerySet):
    def visible(self, principal: Optional[Union["User", "APIKey"]]):
        if hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(
                        datastream__thing__workspace__is_private=False,
                        datastream__thing__is_private=False,
                        datastream__is_private=False,
                    )
                    | Q(datastream__thing__workspace__owner=principal)
                    | Q(
                        datastream__thing__workspace__collaborators__user=principal,
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
        elif hasattr(principal, "workspace"):
            return self.filter(
                Q(
                    datastream__thing__workspace__is_private=False,
                    datastream__thing__is_private=False,
                    datastream__is_private=False,
                )
                | Q(
                    datastream__thing__workspace__apikeys=principal,
                    datastream__thing__workspace__apikeys__role__permissions__resource_type__in=[
                        "*",
                        "Observation",
                    ],
                    datastream__thing__workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.filter(
                Q(
                    datastream__thing__workspace__is_private=False,
                    datastream__thing__is_private=False,
                    datastream__is_private=False,
                )
            )

    def removable(self, principal: Optional[Union["User", "APIKey"]]):
        if hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(datastream__thing__workspace__owner=principal)
                    | Q(
                        datastream__thing__workspace__collaborators__user=principal,
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
        elif hasattr(principal, "workspace"):
            return self.filter(
                datastream__thing__workspace__apikeys=principal,
                datastream__thing__workspace__apikeys__role__permissions__resource_type__in=[
                    "*",
                    "Observation",
                ],
                datastream__thing__workspace__apikeys__role__permissions__permission_type__in=[
                    "*",
                    "delete",
                ],
            )
        else:
            return self.none()

    def bulk_copy(self, observations, batch_size=100_000):
        obs_table_sql = connection.ops.quote_name(self.model._meta.db_table)  # noqa
        obs_fields = [field.column for field in self.model._meta.fields]
        quoted_obs_fields = [connection.ops.quote_name(field) for field in obs_fields]
        obs_fields_sql = ", ".join(quoted_obs_fields)

        rq_model = Observation.result_qualifiers.through
        rq_table_sql = connection.ops.quote_name(rq_model._meta.db_table)  # noqa
        rq_fields = ["observation_id", "result_qualifier_id"]
        rq_fields_sql = ", ".join([connection.ops.quote_name(f) for f in rq_fields])

        obs_attr_getters = [operator.attrgetter(field) for field in obs_fields]
        rq_attr_getters = [operator.attrgetter(field) for field in rq_fields]

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
                f"COPY {obs_table_sql} ({obs_fields_sql}) FROM STDIN"
            ) as copy:
                buffer = io.StringIO()
                for i in range(0, len(observations), batch_size):
                    batch = observations[i : i + batch_size]
                    lines = []
                    for obs in batch:
                        line = "\t".join(
                            escape_pg_copy(getter(obs))
                            for field, getter in zip(obs_fields, obs_attr_getters)
                        )
                        lines.append(line)
                    buffer.write("\n".join(lines) + "\n")
                    buffer.seek(0)
                    copy.write(buffer.read())
                    buffer.truncate(0)
                    buffer.seek(0)

            with cursor.copy(
                f"COPY {rq_table_sql} ({rq_fields_sql}) FROM STDIN"
            ) as copy:
                buffer = io.StringIO()
                for i in range(0, len(observations), batch_size):
                    batch = observations[i : i + batch_size]
                    lines = []
                    for obs in batch:
                        pass  # What to do here?
                    buffer.write("\n".join(lines) + "\n")
                    buffer.seek(0)
                    copy.write(buffer.read())
                    buffer.truncate(0)
                    buffer.seek(0)

        return observations


class Observation(models.Model, PermissionChecker):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    datastream = models.ForeignKey(Datastream, on_delete=models.DO_NOTHING)
    phenomenon_time = models.DateTimeField()
    result = models.FloatField()
    result_time = models.DateTimeField(null=True, blank=True)
    quality_code = models.CharField(max_length=255, null=True, blank=True)
    result_qualifiers = models.ManyToManyField(
        ResultQualifier,
        through="ObservationResultQualifier",
        related_name="observations"
    )

    @property
    def result_qualifier_ids(self):
        if hasattr(self, "_pending_result_qualifier_ids"):
            return list(self._pending_result_qualifier_ids)
        if self.pk is None:
            return []
        return list(self.result_qualifiers.values_list("id", flat=True))

    @result_qualifier_ids.setter
    def result_qualifier_ids(self, ids):
        if self.pk is None:
            self._pending_result_qualifier_ids = ids
        else:
            self.result_qualifiers.set(ids)

    objects = ObservationQuerySet.as_manager()

    @classmethod
    def can_principal_create(
        cls, principal: Optional[Union["User", "APIKey"]], workspace: "Workspace"
    ):
        return cls.check_create_permissions(
            principal=principal, workspace=workspace, resource_type="Observation"
        )

    @classmethod
    def can_principal_delete(
        cls, principal: Optional[Union["User", "APIKey"]], workspace: "Workspace"
    ):
        if not principal:
            return False

        if hasattr(principal, "account_type"):
            if principal.account_type in [
                "admin",
                "staff",
            ]:
                return True

            if workspace.owner == principal:
                return True

            permissions = Permission.objects.filter(
                role__collaborator_assignments__user=principal,
                role__collaborator_assignments__workspace=workspace,
                resource_type__in=["*", "Observation"],
            ).values_list("permission_type", flat=True)

        elif hasattr(principal, "workspace"):
            if not workspace or principal.workspace != workspace:
                return False

            permissions = Permission.objects.filter(
                role=principal.role,
                resource_type__in=["*", "Observation"],
            ).values_list("permission_type", flat=True)

        else:
            return False

        return any(perm in permissions for perm in ["*", "delete"])

    def get_principal_permissions(
        self, principal: Optional[Union["User", "APIKey"]]
    ) -> list[Literal["edit", "delete", "view"]]:
        permissions = self.check_object_permissions(
            principal=principal,
            workspace=self.datastream.thing.workspace,
            resource_type="Observation",
        )

        if (
            not self.datastream.thing.workspace.is_private
            and not self.datastream.thing.is_private
            and not self.datastream.is_private
            and "view" not in list(permissions)
        ):
            permissions = list(permissions) + ["view"]

        return permissions

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datastream_id", "phenomenon_time"],
                name="unique_datastream_id_phenomenon_time",
            )
        ]


class ObservationResultQualifier(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.DO_NOTHING)
    result_qualifier = models.ForeignKey(ResultQualifier, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["observation_id", "result_qualifier_id"],
                name="unique_observation_id_result_qualifier_id",
            )
        ]
