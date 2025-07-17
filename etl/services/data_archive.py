import uuid
from typing import Literal, Optional, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from iam.models import APIKey
from sta.services.datastream import DatastreamService
from etl.models import DataArchive
from etl.schemas import DataArchivePostBody, DataArchivePatchBody
from etl.schemas.data_archive import (
    DataArchiveFields,
    DataArchiveSummaryResponse,
    DataArchiveDetailResponse,
)
from etl.schemas.orchestration_configuration import (
    OrchestrationConfigurationOrderByFields,
)
from api.service import ServiceUtils

from etl.schemas.orchestration_configuration import (
    OrchestrationConfigurationScheduleFields,
    OrchestrationConfigurationStatusFields,
)

from .orchestration_configuration import OrchestrationConfigurationUtils

User = get_user_model()

datastream_service = DatastreamService()


class DataArchiveService(ServiceUtils, OrchestrationConfigurationUtils):

    def get_data_archive_for_action(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        expand_related: Optional[bool] = None,
        raise_400: bool = False,
    ):
        try:
            data_archive = DataArchive.objects
            if expand_related:
                data_archive = self.select_expanded_fields(data_archive)
            data_archive = data_archive.get(pk=uid)
        except DataArchive.DoesNotExist:
            raise HttpError(
                404 if not raise_400 else 400, "Data archive does not exist"
            )

        data_archive_permissions = data_archive.get_principal_permissions(
            principal=principal
        )

        if "view" not in data_archive_permissions:
            raise HttpError(
                404 if not raise_400 else 400, "Data archive does not exist"
            )

        if action not in data_archive_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this data archive",
            )

        return data_archive

    @staticmethod
    def select_expanded_fields(queryset: QuerySet) -> QuerySet:
        return queryset.select_related(
            "workspace", "orchestration_system"
        ).prefetch_related("datastreams")

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
        expand_related: Optional[bool] = None,
    ):
        queryset = DataArchive.objects

        for field in [
            "workspace_id",
            "orchestration_system_id",
            "datastreams__id",
            "last_run_successful",
            "last_run__lte",
            "last_run__gte",
            "next_run__lte",
            "next_run__gte",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(OrchestrationConfigurationOrderByFields)),
            )

        if expand_related:
            queryset = self.select_expanded_fields(queryset)

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        return [
            (
                DataArchiveDetailResponse.model_validate(data_source)
                if expand_related
                else DataArchiveSummaryResponse.model_validate(data_source)
            )
            for data_source in queryset.all()
        ]

    def get(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        expand_related: Optional[bool] = None,
    ):
        data_archive = self.get_data_archive_for_action(
            principal=principal, uid=uid, action="view", expand_related=expand_related
        )

        return (
            DataArchiveDetailResponse.model_validate(data_archive)
            if expand_related
            else DataArchiveSummaryResponse.model_validate(data_archive)
        )

    def create(
        self,
        principal: User | APIKey,
        data: DataArchivePostBody,
        expand_related: Optional[bool] = None,
    ):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not DataArchive.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this data archive"
            )

        orchestration_system = self.validate_orchestration_system(
            principal=principal,
            orchestration_system_id=data.orchestration_system_id,
            workspace=workspace,
        )

        if data.schedule is not None:
            self.validate_scheduling(
                crontab=data.schedule.crontab,
                interval=data.schedule.interval,
                interval_units=data.schedule.interval_units,
            )

        data_archive = DataArchive.objects.create(
            workspace=workspace,
            orchestration_system=orchestration_system,
            **data.dict(include=set(DataArchiveFields.model_fields.keys())),
            **(
                data.schedule.dict(
                    include=set(
                        OrchestrationConfigurationScheduleFields.model_fields.keys()
                    )
                )
                if data.schedule
                else {}
            ),
            **(
                data.status.dict(
                    include=set(
                        OrchestrationConfigurationStatusFields.model_fields.keys()
                    )
                )
                if data.status
                else {}
            ),
        )

        if data.datastream_ids:
            for datastream_id in data.datastream_ids:
                self.link_datastream(
                    principal=principal,
                    uid=data_archive.id,
                    datastream_id=datastream_id,
                )

        return self.get(
            principal=principal, uid=data_archive.id, expand_related=expand_related
        )

    def update(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        data: DataArchivePatchBody,
        expand_related: Optional[bool] = None,
    ):
        data_archive = self.get_data_archive_for_action(
            principal=principal, uid=uid, action="edit"
        )
        data_archive_data = data.dict(
            include=set(DataArchiveFields.model_fields.keys()),
            exclude_unset=True,
        )

        if data.orchestration_system_id:
            orchestration_system = self.validate_orchestration_system(
                principal=principal,
                orchestration_system_id=data.orchestration_system_id,
                workspace=data_archive.workspace,
            )
            data_archive_data["orchestration_system_id"] = orchestration_system.id

        if "schedule" in data.model_fields_set:
            if data.schedule is not None:
                self.validate_scheduling(
                    crontab=data.schedule.crontab,
                    interval=data.schedule.interval,
                    interval_units=data.schedule.interval_units,
                )
                data_archive_data.update(
                    data.schedule.dict(
                        include=set(
                            OrchestrationConfigurationScheduleFields.model_fields.keys()
                        )
                    )
                )
            else:
                data_archive_data.update(
                    {
                        key: field.default
                        for key, field in OrchestrationConfigurationScheduleFields.model_fields.items()
                    }
                )

        if "status" in data.model_fields_set:
            if data.status is not None:
                data_archive_data.update(
                    data.status.dict(
                        include=set(
                            OrchestrationConfigurationStatusFields.model_fields.keys()
                        )
                    )
                )
            else:
                data_archive_data.update(
                    {
                        key: False if key == "paused" else field.default
                        for key, field in OrchestrationConfigurationStatusFields.model_fields.items()
                    }
                )

        for field, value in data_archive_data.items():
            setattr(data_archive, field, value)

        data_archive.save()

        return self.get(
            principal=principal, uid=data_archive.id, expand_related=expand_related
        )

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        data_archive = self.get_data_archive_for_action(
            principal=principal, uid=uid, action="delete", expand_related=True
        )

        data_archive.delete()

        return "Data archive deleted"

    def link_datastream(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        datastream_id: uuid.UUID,
    ):
        data_archive = self.get_data_archive_for_action(
            principal=principal, uid=uid, action="edit"
        )
        datastream = datastream_service.get_datastream_for_action(
            principal=principal, uid=datastream_id, action="edit"
        )

        if data_archive.datastreams.filter(pk=datastream.id).exists():
            raise HttpError(
                400, "Datastream has already been linked to this data archive"
            )

        if data_archive.workspace != datastream.thing.workspace:
            raise HttpError(
                400, "The datastream must share a workspace with the data archive"
            )

        data_archive.datastreams.add(datastream)

        return "Data archive configured for datastream"

    def unlink_datastream(
        self, principal: User | APIKey, uid: uuid.UUID, datastream_id: uuid.UUID
    ):
        data_archive = self.get_data_archive_for_action(
            principal=principal, uid=uid, action="edit"
        )
        datastream = datastream_service.get_datastream_for_action(
            principal=principal, uid=datastream_id, action="edit"
        )

        if not data_archive.datastreams.filter(pk=datastream.id).exists():
            raise HttpError(
                400, "The given data archive is not configured for this datastream"
            )

        data_archive.datastreams.remove(datastream)

        return "Datastream unlinked from data archive"
