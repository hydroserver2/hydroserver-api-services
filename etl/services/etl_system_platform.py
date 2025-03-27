import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from etl.models import EtlSystemPlatform
from etl.schemas import EtlSystemPlatformPostBody, EtlSystemPlatformPatchBody
from etl.schemas.etl_system_platform import EtlSystemPlatformFields

User = get_user_model()


class EtlSystemPlatformService(ServiceUtils):
    @staticmethod
    def get_etl_system_platform_for_action(
        user: User, uid: uuid.UUID, action: Literal["view", "edit", "delete"]
    ):
        try:
            etl_system_platform = EtlSystemPlatform.objects.select_related(
                "workspace"
            ).get(pk=uid)
        except EtlSystemPlatform.DoesNotExist:
            raise HttpError(404, "ETL system platform does not exist")

        etl_system_platform_permissions = etl_system_platform.get_user_permissions(
            user=user
        )

        if "view" not in etl_system_platform_permissions:
            raise HttpError(404, "ETL system platform does not exist")

        if action not in etl_system_platform_permissions:
            raise HttpError(
                403, f"You do not have permission to {action} this ETL system platform"
            )

        return etl_system_platform

    @staticmethod
    def list(user: Optional[User], workspace_id: Optional[uuid.UUID]):
        queryset = EtlSystemPlatform.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(user=user).distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_etl_system_platform_for_action(
            user=user, uid=uid, action="view"
        )

    def create(self, user: User, data: EtlSystemPlatformPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not EtlSystemPlatform.can_user_create(user=user, workspace=workspace):
            raise HttpError(
                403, "You do not have permission to create this ETL system platform"
            )

        etl_system_platform = EtlSystemPlatform.objects.create(
            workspace=workspace,
            **data.dict(include=set(EtlSystemPlatformFields.model_fields.keys())),
        )

        return etl_system_platform

    def update(self, user: User, uid: uuid.UUID, data: EtlSystemPlatformPatchBody):
        etl_system_platform = self.get_etl_system_platform_for_action(
            user=user, uid=uid, action="edit"
        )
        etl_system_platform_data = data.dict(
            include=set(EtlSystemPlatformFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in etl_system_platform_data.items():
            setattr(etl_system_platform, field, value)

        etl_system_platform.save()

        return etl_system_platform

    def delete(self, user: User, uid: uuid.UUID):
        etl_system_platform = self.get_etl_system_platform_for_action(
            user=user, uid=uid, action="delete"
        )

        if etl_system_platform.etl_systems.exists():
            raise HttpError(409, "ETL system platform has one or more active instances")

        etl_system_platform.delete()

        return "ETL system platform deleted"
