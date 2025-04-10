import uuid
from typing import Literal, Optional
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.services.datastream import DatastreamService
from etl.models import DataArchive
from etl.schemas import DataArchivePostBody, DataArchivePatchBody
from etl.schemas.data_archive import DataArchiveFields

from etl.schemas.orchestration_configuration import (
    OrchestrationConfigurationScheduleFields,
    OrchestrationConfigurationStatusFields,
)

from .orchestration_configuration import OrchestrationConfigurationUtils

User = get_user_model()

datastream_service = DatastreamService()


class DataArchiveService(ServiceUtils, OrchestrationConfigurationUtils):
    @staticmethod
    def get_data_archive_for_action(
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        fetch_datastreams: bool = False,
        raise_400: bool = False,
    ):
        try:
            data_archive = DataArchive.objects.select_related(
                "workspace",
                "orchestration_system",
            )
            if fetch_datastreams:
                data_archive = data_archive.prefetch_related("datastreams")
            data_archive = data_archive.get(pk=uid)
        except DataArchive.DoesNotExist:
            raise HttpError(
                404 if not raise_400 else 400, "Data archive does not exist"
            )

        data_archive_permissions = data_archive.get_user_permissions(user=user)

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
    def list(
        user: User,
        workspace_id: Optional[uuid.UUID],
        orchestration_system_id: Optional[uuid.UUID],
    ):
        queryset = DataArchive.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        if orchestration_system_id:
            queryset = queryset.filter(orchestration_system_id=orchestration_system_id)

        return (
            queryset.select_related("orchestration_system")
            .prefetch_related("datastreams")
            .visible(user=user)
            .distinct()
        )

    def get(self, user: User, uid: uuid.UUID):
        return self.get_data_archive_for_action(
            user=user, uid=uid, action="view", fetch_datastreams=True
        )

    def create(self, user: User, data: DataArchivePostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not DataArchive.can_user_create(user=user, workspace=workspace):
            raise HttpError(
                403, "You do not have permission to create this data archive"
            )

        orchestration_system = self.validate_orchestration_system(
            user=user,
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
                    user=user, uid=data_archive.id, datastream_id=datastream_id
                )

        return data_archive

    def update(self, user: User, uid: uuid.UUID, data: DataArchivePatchBody):
        data_archive = self.get_data_archive_for_action(
            user=user, uid=uid, action="edit"
        )
        data_archive_data = data.dict(
            include=set(DataArchiveFields.model_fields.keys()),
            exclude_unset=True,
        )

        if data.orchestration_system_id:
            orchestration_system = self.validate_orchestration_system(
                user=user,
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

        return data_archive

    def delete(self, user: User, uid: uuid.UUID):
        data_archive = self.get_data_archive_for_action(
            user=user, uid=uid, action="delete"
        )

        data_archive.delete()

        return "Data archive deleted"

    def link_datastream(
        self,
        user: User,
        uid: uuid.UUID,
        datastream_id: uuid.UUID,
    ):
        data_archive = self.get_data_archive_for_action(
            user=user, uid=uid, action="edit"
        )
        datastream = datastream_service.get_datastream_for_action(
            user=user, uid=datastream_id, action="edit"
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

    def unlink_datastream(self, user: User, uid: uuid.UUID, datastream_id: uuid.UUID):
        data_archive = self.get_data_archive_for_action(
            user=user, uid=uid, action="edit"
        )
        datastream = datastream_service.get_datastream_for_action(
            user=user, uid=datastream_id, action="edit"
        )

        if not data_archive.datastreams.filter(pk=datastream.id).exists():
            raise HttpError(
                400, "The given data archive is not configured for this datastream"
            )

        data_archive.datastreams.remove(datastream)

        return "Datastream unlinked from data archive"
