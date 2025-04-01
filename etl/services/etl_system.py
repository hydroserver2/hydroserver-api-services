import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from etl.models import EtlSystem
from etl.schemas import EtlSystemPostBody, EtlSystemPatchBody
from etl.schemas.etl_system import EtlSystemFields
from .etl_system_platform import EtlSystemPlatformService

User = get_user_model()
etl_system_platform_service = EtlSystemPlatformService()


class EtlSystemService(ServiceUtils):
    @staticmethod
    def get_etl_system_for_action(
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        raise_400: bool = False,
    ):
        try:
            etl_system = EtlSystem.objects.select_related("workspace").get(pk=uid)
        except EtlSystem.DoesNotExist:
            raise HttpError(404 if not raise_400 else 400, "ETL system does not exist")

        etl_system_permissions = etl_system.get_user_permissions(user=user)

        if "view" not in etl_system_permissions:
            raise HttpError(404 if not raise_400 else 400, "ETL system does not exist")

        if action not in etl_system_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this ETL system",
            )

        return etl_system

    @staticmethod
    def list(
        user: Optional[User],
        workspace_id: Optional[uuid.UUID] = None,
        etl_system_platform_id: Optional[uuid.UUID] = None,
    ):
        queryset = EtlSystem.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        if etl_system_platform_id:
            queryset = queryset.filter(etl_system_platform_id=etl_system_platform_id)

        return queryset.visible(user=user).distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_etl_system_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: EtlSystemPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not EtlSystem.can_user_create(user=user, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this ETL system")

        etl_system_platform = self.handle_http_404_error(
            etl_system_platform_service.get, user=user, uid=data.etl_system_platform_id
        )

        if etl_system_platform.workspace and etl_system_platform.workspace != workspace:
            if not workspace:
                workspace = etl_system_platform.workspace
            else:
                raise HttpError(
                    400,
                    "ETL systems must share a workspace with the ETL system platform",
                )

        etl_system = EtlSystem.objects.create(
            workspace=workspace,
            etl_system_platform=etl_system_platform,
            **data.dict(include=set(EtlSystemFields.model_fields.keys())),
        )

        return etl_system

    def update(self, user: User, uid: uuid.UUID, data: EtlSystemPatchBody):
        etl_system = self.get_etl_system_for_action(user=user, uid=uid, action="edit")
        etl_system_data = data.dict(
            include=set(EtlSystemFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in etl_system_data.items():
            setattr(etl_system, field, value)

        etl_system.save()

        return etl_system

    def delete(self, user: User, uid: uuid.UUID):
        etl_system = self.get_etl_system_for_action(user=user, uid=uid, action="delete")

        if etl_system.data_sources.exists():
            raise HttpError(409, "ETL system in use by one or more data sources")

        etl_system.delete()

        return "ETL system deleted"
