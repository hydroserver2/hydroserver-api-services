import uuid
from typing import Literal, Optional
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.services.datastream import DatastreamService
from etl.models import DataSource
from etl.schemas import DataSourcePostBody, DataSourcePatchBody
from etl.schemas.data_source import DataSourceFields

from etl.schemas.orchestration_configuration import (
    OrchestrationConfigurationScheduleFields,
    OrchestrationConfigurationStatusFields,
)

from .orchestration_configuration import OrchestrationConfigurationUtils

User = get_user_model()

datastream_service = DatastreamService()


class DataSourceService(ServiceUtils, OrchestrationConfigurationUtils):
    @staticmethod
    def get_data_source_for_action(
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        fetch_datastreams: bool = False,
        raise_400: bool = False,
    ):
        try:
            data_source = DataSource.objects.select_related(
                "workspace",
                "orchestration_system",
            )
            if fetch_datastreams:
                data_source = data_source.prefetch_related("datastreams")
            data_source = data_source.get(pk=uid)
        except DataSource.DoesNotExist:
            raise HttpError(404 if not raise_400 else 400, "Data source does not exist")

        data_source_permissions = data_source.get_user_permissions(user=user)

        if "view" not in data_source_permissions:
            raise HttpError(404 if not raise_400 else 400, "Data source does not exist")

        if action not in data_source_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this data source",
            )

        return data_source

    @staticmethod
    def list(
        user: User,
        workspace_id: Optional[uuid.UUID],
        orchestration_system_id: Optional[uuid.UUID],
    ):
        queryset = DataSource.objects

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
        return self.get_data_source_for_action(
            user=user, uid=uid, action="view", fetch_datastreams=True
        )

    def create(self, user: User, data: DataSourcePostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not DataSource.can_user_create(user=user, workspace=workspace):
            raise HttpError(
                403, "You do not have permission to create this data source"
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

        data_source = DataSource.objects.create(
            workspace=workspace,
            orchestration_system=orchestration_system,
            **data.dict(include=set(DataSourceFields.model_fields.keys())),
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
                    user=user, uid=data_source.id, datastream_id=datastream_id
                )

        return data_source

    def update(self, user: User, uid: uuid.UUID, data: DataSourcePatchBody):
        data_source = self.get_data_source_for_action(user=user, uid=uid, action="edit")
        data_source_data = data.dict(
            include=set(DataSourceFields.model_fields.keys()),
            exclude_unset=True,
        )

        if data.orchestration_system_id:
            orchestration_system = self.validate_orchestration_system(
                user=user,
                orchestration_system_id=data.orchestration_system_id,
                workspace=data_source.workspace,
            )
            data_source_data["orchestration_system_id"] = orchestration_system.id

        if "schedule" in data.model_fields_set:
            if data.schedule is not None:
                self.validate_scheduling(
                    crontab=data.schedule.crontab,
                    interval=data.schedule.interval,
                    interval_units=data.schedule.interval_units,
                )
                data_source_data.update(
                    data.schedule.dict(
                        include=set(
                            OrchestrationConfigurationScheduleFields.model_fields.keys()
                        ),
                        exclude_unset=True,
                    )
                )
            else:
                data_source_data.update(
                    {
                        key: field.default
                        for key, field in OrchestrationConfigurationScheduleFields.model_fields.items()
                    }
                )

        if "status" in data.model_fields_set:
            if data.status is not None:
                data_source_data.update(
                    data.status.dict(
                        include=set(
                            OrchestrationConfigurationStatusFields.model_fields.keys()
                        ),
                        exclude_unset=True,
                    )
                )
            else:
                data_source_data.update(
                    {
                        key: False if key == "paused" else field.default
                        for key, field in OrchestrationConfigurationStatusFields.model_fields.items()
                    }
                )

        for field, value in data_source_data.items():
            setattr(data_source, field, value)

        data_source.save()

        return data_source

    def delete(self, user: User, uid: uuid.UUID):
        data_source = self.get_data_source_for_action(
            user=user, uid=uid, action="delete"
        )

        data_source.delete()

        return "Data source deleted"

    def link_datastream(
        self,
        user: User,
        uid: uuid.UUID,
        datastream_id: uuid.UUID,
    ):
        data_source = self.get_data_source_for_action(user=user, uid=uid, action="edit")
        datastream = datastream_service.get_datastream_for_action(
            user=user, uid=datastream_id, action="edit"
        )

        if datastream.data_source is not None:
            raise HttpError(400, "Datastream has already been linked to a data source")

        if data_source.workspace != datastream.thing.workspace:
            raise HttpError(
                400, "The datastream must share a workspace with the data source"
            )

        datastream.data_source = data_source
        datastream.save()

        return "Data source configured for datastream"

    def unlink_datastream(self, user: User, uid: uuid.UUID, datastream_id: uuid.UUID):
        data_source = self.get_data_source_for_action(user=user, uid=uid, action="edit")
        datastream = datastream_service.get_datastream_for_action(
            user=user, uid=datastream_id, action="edit"
        )

        if datastream.data_source != data_source:
            raise HttpError(
                400, "The given data source is not configured for this datastream"
            )

        datastream.data_source = None
        datastream.save()

        return "Datastream unlinked from data source"
