import uuid
from typing import Optional, Literal
from jsonschema.validators import validator_for
from jsonschema.exceptions import SchemaError
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.db.models import Q
from iam.services.utils import ServiceUtils
from etl.models import EtlConfiguration, EtlSystemPlatform, DataSource, LinkedDatastream
from etl.schemas import EtlConfigurationPostBody, EtlConfigurationPatchBody
from etl.schemas.etl_configuration import EtlConfigurationFields
from etl.services.etl_system_platform import EtlSystemPlatformService

User = get_user_model()
etl_system_platform_service = EtlSystemPlatformService()


class EtlConfigurationService(ServiceUtils):
    @staticmethod
    def get_etl_configuration_for_action(
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        etl_system_platform_id: Optional[uuid.UUID] = None,
        raise_400: bool = False,
    ):
        if (
            etl_system_platform_id
            and not EtlSystemPlatform.objects.filter(pk=etl_system_platform_id).exists()
        ):
            raise HttpError(
                404 if not raise_400 else 400, "ETL system platform does not exist"
            )

        try:
            etl_configuration = EtlConfiguration.objects.select_related(
                "etl_system_platform__workspace"
            ).get(pk=uid)
        except EtlConfiguration.DoesNotExist:
            raise HttpError(
                404 if not raise_400 else 400, "ETL configuration does not exist"
            )

        etl_configuration_permissions = etl_configuration.get_user_permissions(
            user=user
        )

        if "view" not in etl_configuration_permissions:
            raise HttpError(
                404 if not raise_400 else 400, "ETL configuration does not exist"
            )

        if action not in etl_configuration_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this ETL configuration",
            )

        return etl_configuration

    @staticmethod
    def validate_configuration(configuration):
        validator = validator_for(configuration)
        validator.check_schema(configuration)

    @staticmethod
    def list(
        user: Optional[User],
        workspace_id: Optional[uuid.UUID],
        etl_system_platform_id: Optional[uuid.UUID],
    ):
        queryset = EtlConfiguration.objects

        if workspace_id:
            queryset = queryset.filter(etl_system_platform__workspace_id=workspace_id)

        if etl_system_platform_id:
            queryset = queryset.filter(etl_system_platform_id=etl_system_platform_id)

        return queryset.visible(user=user).distinct()

    def get(
        self, user: Optional[User], uid: uuid.UUID, etl_system_platform_id: uuid.UUID
    ):
        return self.get_etl_configuration_for_action(
            user=user,
            uid=uid,
            etl_system_platform_id=etl_system_platform_id,
            action="view",
        )

    def create(
        self,
        user: User,
        etl_system_platform_id: uuid.UUID,
        data: EtlConfigurationPostBody,
    ):
        etl_system_platform = (
            etl_system_platform_service.get_etl_system_platform_for_action(
                user=user, uid=etl_system_platform_id, action="view"
            )
        )

        if not etl_system_platform.workspace or not EtlConfiguration.can_user_create(
            user=user, workspace=etl_system_platform.workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this ETL configuration"
            )

        try:
            self.validate_configuration(data.etl_configuration_schema)
        except SchemaError as e:
            raise HttpError(400, str(e))

        etl_configuration = EtlConfiguration.objects.create(
            etl_system_platform=etl_system_platform,
            **data.dict(include=set(EtlConfigurationFields.model_fields.keys())),
        )

        return etl_configuration

    def update(
        self,
        user: User,
        etl_system_platform_id: uuid.UUID,
        uid: uuid.UUID,
        data: EtlConfigurationPatchBody,
    ):
        etl_configuration = self.get_etl_configuration_for_action(
            user=user,
            uid=uid,
            etl_system_platform_id=etl_system_platform_id,
            action="edit",
        )
        etl_configuration_data = data.dict(
            include=set(EtlConfigurationFields.model_fields.keys()), exclude_unset=True
        )

        try:
            if etl_configuration_data.get("etl_configuration_schema"):
                self.validate_configuration(data.etl_configuration_schema)
        except SchemaError as e:
            raise HttpError(400, str(e))

        for field, value in etl_configuration_data.items():
            setattr(etl_configuration, field, value)

        etl_configuration.save()

        return etl_configuration

    def delete(self, user: User, etl_system_platform_id: uuid.UUID, uid: uuid.UUID):
        etl_configuration = self.get_etl_configuration_for_action(
            user=user,
            uid=uid,
            etl_system_platform_id=etl_system_platform_id,
            action="delete",
        )

        if DataSource.objects.filter(
            Q(extractor_configuration=etl_configuration) |
            Q(transformer_configuration=etl_configuration) |
            Q(loader_configuration=etl_configuration)
        ).exists():
            raise HttpError(409, "ETL configuration in use by one or more data sources")

        if LinkedDatastream.objects.filter(
            Q(extractor_configuration=etl_configuration) |
            Q(transformer_configuration=etl_configuration) |
            Q(loader_configuration=etl_configuration)
        ).exists():
            raise HttpError(409, "ETL configuration in use by one or more datastreams")

        etl_configuration.delete()

        return "ETL configuration deleted"
