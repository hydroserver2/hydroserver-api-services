import uuid
from typing import Literal, Optional
from jsonschema.validators import validate
from jsonschema.exceptions import SchemaError, ValidationError
from croniter import croniter
from datetime import datetime
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import Workspace
from iam.services.utils import ServiceUtils
from sta.services.datastream import DatastreamService
from etl.models import DataSource, LinkedDatastream, EtlSystemPlatform
from etl.schemas import (
    DataSourcePostBody,
    DataSourcePatchBody,
    LinkedDatastreamFields,
    LinkedDatastreamPostBody,
    LinkedDatastreamPatchBody,
)
from etl.schemas.data_source import DataSourceFields
from etl.services.etl_configuration import EtlConfigurationService
from etl.services.etl_system import EtlSystemService

User = get_user_model()

datastream_service = DatastreamService()
etl_system_service = EtlSystemService()
etl_configuration_service = EtlConfigurationService()


class DataSourceService(ServiceUtils):
    @staticmethod
    def get_data_source_for_action(
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        fetch_linked_datastreams: bool = False,
        raise_400: bool = False,
    ):
        try:
            data_source = DataSource.objects.select_related("workspace")
            if fetch_linked_datastreams:
                data_source = data_source.prefetch_related(
                    "linked_datastreams", "linked_datastreams__datastream"
                )
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

    def get_linked_datastream_for_action(
        self,
        user: User,
        data_source_id: uuid.UUID,
        datastream_id: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        data_source = self.get_data_source_for_action(
            user=user, uid=data_source_id, action=action, fetch_linked_datastreams=True
        )

        try:
            linked_datastream = data_source.linked_datastreams.select_related(
                "data_source", "datastream"
            ).get(datastream_id=datastream_id)
        except LinkedDatastream.DoesNotExist:
            raise HttpError(
                400, "The given datastream is not linked to this data source"
            )

        return linked_datastream

    @staticmethod
    def validate_etl_system(user: User, etl_system_id: uuid.UUID, workspace: Workspace):
        etl_system = etl_system_service.get_etl_system_for_action(
            user=user, uid=etl_system_id, action="view", raise_400=True
        )

        if etl_system.workspace not in {workspace, None}:
            raise HttpError(
                400, "The given ETL system cannot be associated with this data source"
            )

        return etl_system

    @staticmethod
    def validate_etl_configuration(
        user: User,
        etl_configuration_id: uuid.UUID,
        etl_system_platform: EtlSystemPlatform,
        etl_configuration_settings: dict,
    ):
        if not etl_configuration_id:
            return None

        etl_configuration = etl_configuration_service.get_etl_configuration_for_action(
            user=user, uid=etl_configuration_id, action="view", raise_400=True
        )

        if etl_configuration.etl_system_platform != etl_system_platform:
            raise HttpError(400, "The given ETL configuration cannot be used")

        if etl_configuration:
            try:
                validate(
                    etl_configuration_settings,
                    etl_configuration.etl_configuration_schema,
                )
            except (ValidationError, SchemaError) as e:
                raise HttpError(400, str(e))

        return etl_configuration

    @staticmethod
    def validate_scheduling(
        etl_system, crontab=None, interval=None, interval_units=None, data_source=None
    ):
        if crontab and not etl_system.etl_system_platform.crontab_schedule_supported:
            raise HttpError(
                400, "Crontab schedule not supported by ETL system platform"
            )
        if (
            interval or interval_units
        ) and not etl_system.etl_system_platform.interval_schedule_supported:
            raise HttpError(
                400, "Interval schedule not supported by ETL system platform"
            )

        if crontab and (interval or interval_units):
            raise HttpError(
                400, "Only one of crontab schedule or interval schedule can be set"
            )

        if crontab:
            try:
                croniter(crontab, datetime.now())
            except (ValueError, AttributeError):
                raise HttpError(400, "Invalid crontab schedule")

        if interval or interval_units:
            if not (interval and interval_units):
                raise HttpError(
                    400, "Both interval and interval units must be provided"
                )
            if data_source and data_source.crontab and crontab is not None:
                raise HttpError(
                    400, "Only one of crontab schedule or interval schedule can be set"
                )

    @staticmethod
    def list(
        user: User,
        workspace_id: Optional[uuid.UUID],
        etl_system_platform_id: Optional[uuid.UUID],
        etl_system_id: Optional[uuid.UUID],
    ):
        queryset = DataSource.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        if etl_system_platform_id:
            queryset = queryset.filter(
                etl_system__etl_system_platform_id=etl_system_platform_id
            )
        if etl_system_id:
            queryset = queryset.filter(etl_system_id=etl_system_id)

        return (
            queryset.prefetch_related(
                "linked_datastreams", "linked_datastreams__datastream"
            )
            .visible(user=user)
            .distinct()
        )

    def get(self, user: User, uid: uuid.UUID):
        return self.get_data_source_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: DataSourcePostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not DataSource.can_user_create(user=user, workspace=workspace):
            raise HttpError(
                403, "You do not have permission to create this data source"
            )

        etl_system = self.validate_etl_system(
            user=user, etl_system_id=data.etl_system_id, workspace=workspace
        )
        self.validate_etl_configuration(
            user=user,
            etl_configuration_id=data.etl_configuration_id,
            etl_system_platform=etl_system.etl_system_platform,
            etl_configuration_settings=data.etl_configuration_settings,
        )
        self.validate_scheduling(
            etl_system=etl_system,
            crontab=data.crontab,
            interval=data.interval,
            interval_units=data.interval_units,
        )

        data_source = DataSource.objects.create(
            workspace=workspace,
            **data.dict(include=set(DataSourceFields.model_fields.keys())),
        )

        return data_source

    def update(self, user: User, uid: uuid.UUID, data: DataSourcePatchBody):
        data_source = self.get_data_source_for_action(user=user, uid=uid, action="edit")
        data_source_data = data.dict(
            include=set(DataSourceFields.model_fields.keys()), exclude_unset=True
        )

        etl_system = self.validate_etl_system(
            user=user,
            etl_system_id=data_source.etl_system_id,
            workspace=data_source.workspace,
        )
        self.validate_etl_configuration(
            user=user,
            etl_configuration_id=data_source_data.get(
                "etl_configuration_id", data_source.etl_configuration_id
            ),
            etl_system_platform=etl_system.etl_system_platform,
            etl_configuration_settings=data_source_data.get(
                "etl_configuration_settings", data_source.etl_configuration_settings
            ),
        )
        self.validate_scheduling(
            etl_system=etl_system,
            crontab=data_source_data.get("crontab", data_source.crontab),
            interval=data_source_data.get("interval", data_source.interval),
            interval_units=data_source_data.get(
                "interval_units", data_source.interval_units
            ),
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

    def list_linked_datastreams(self, user: User, uid: uuid.UUID):
        data_source = self.get_data_source_for_action(
            user=user, uid=uid, action="view", fetch_linked_datastreams=True
        )

        return data_source.linked_datastreams.all()

    def link_datastream(
        self,
        user: User,
        uid: uuid.UUID,
        datastream_id: uuid.UUID,
        data: LinkedDatastreamPostBody,
    ):
        data_source = self.get_data_source_for_action(user=user, uid=uid, action="edit")
        datastream = datastream_service.get_datastream_for_action(
            user=user, uid=datastream_id, action="edit"
        )

        if getattr(datastream, "data_source", None) is not None:
            raise HttpError(400, "Datastream has already been linked to a data source")

        if data_source.workspace != datastream.thing.workspace:
            raise HttpError(
                400, "The datastream must share a workspace with the data source"
            )

        self.validate_etl_configuration(
            user=user,
            etl_configuration_id=data.etl_configuration_id,
            etl_system_platform=data_source.etl_system.etl_system_platform,
            etl_configuration_settings=data.etl_configuration_settings,
        )

        linked_datastream = LinkedDatastream.objects.create(
            data_source=data_source,
            datastream=datastream,
            **data.dict(include=set(LinkedDatastreamFields.model_fields.keys())),
        )
        linked_datastream.datastream = datastream

        return linked_datastream

    def get_linked_datastream(
        self, user: User, uid: uuid.UUID, datastream_id: uuid.UUID
    ):
        return self.get_linked_datastream_for_action(
            user=user, data_source_id=uid, datastream_id=datastream_id, action="view"
        )

    def update_linked_datastream(
        self,
        user: User,
        uid: uuid.UUID,
        datastream_id: uuid.UUID,
        data: LinkedDatastreamPatchBody,
    ):
        linked_datastream = self.get_linked_datastream_for_action(
            user=user, data_source_id=uid, datastream_id=datastream_id, action="edit"
        )
        linked_datastream_data = data.dict(
            include=set(LinkedDatastreamFields.model_fields.keys()), exclude_unset=True
        )

        self.validate_etl_configuration(
            user=user,
            etl_configuration_id=linked_datastream_data.get(
                "etl_configuration_id", linked_datastream.etl_configuration_id
            ),
            etl_system_platform=linked_datastream.data_source.etl_system.etl_system_platform,
            etl_configuration_settings=linked_datastream_data.get(
                "etl_configuration_settings",
                linked_datastream.etl_configuration_settings,
            ),
        )

        for field, value in linked_datastream_data.items():
            setattr(linked_datastream, field, value)

        linked_datastream.save()

        return linked_datastream

    def unlink_datastream(self, user: User, uid: uuid.UUID, datastream_id: uuid.UUID):
        linked_datastream = self.get_linked_datastream_for_action(
            user=user, data_source_id=uid, datastream_id=datastream_id, action="edit"
        )

        linked_datastream.delete()

        return "Datastream unlinked from data source"
