import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from iam.models import APIKey
from etl.models import OrchestrationSystem
from etl.schemas import OrchestrationSystemPostBody, OrchestrationSystemPatchBody
from etl.schemas.orchestration_system import OrchestrationSystemFields

User = get_user_model()


class OrchestrationSystemService(ServiceUtils):
    @staticmethod
    def get_orchestration_system_for_action(
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        raise_400: bool = False,
    ):
        try:
            orchestration_system = OrchestrationSystem.objects.select_related(
                "workspace"
            ).get(pk=uid)
        except OrchestrationSystem.DoesNotExist:
            raise HttpError(
                404 if not raise_400 else 400, "Orchestration system does not exist"
            )

        orchestration_system_permissions = (
            orchestration_system.get_principal_permissions(principal=principal)
        )

        if "view" not in orchestration_system_permissions:
            raise HttpError(
                404 if not raise_400 else 400, "Orchestration system does not exist"
            )

        if action not in orchestration_system_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this orchestration system",
            )

        return orchestration_system

    @staticmethod
    def list(
        principal: Optional[Union[User, APIKey]],
        workspace_id: Optional[uuid.UUID] = None,
    ):
        queryset = OrchestrationSystem.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(principal=principal).distinct()

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_orchestration_system_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: Union[User, APIKey], data: OrchestrationSystemPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not OrchestrationSystem.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this orchestration system"
            )

        orchestration_system = OrchestrationSystem.objects.create(
            workspace=workspace,
            **data.dict(include=set(OrchestrationSystemFields.model_fields.keys())),
        )

        return orchestration_system

    def update(
        self,
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        data: OrchestrationSystemPatchBody,
    ):
        orchestration_system = self.get_orchestration_system_for_action(
            principal=principal, uid=uid, action="edit"
        )
        orchestration_system_data = data.dict(
            include=set(OrchestrationSystemFields.model_fields.keys()),
            exclude_unset=True,
        )

        for field, value in orchestration_system_data.items():
            setattr(orchestration_system, field, value)

        orchestration_system.save()

        return orchestration_system

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        orchestration_system = self.get_orchestration_system_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if orchestration_system.data_sources.exists():
            raise HttpError(
                409, "Orchestration system in use by one or more data sources"
            )

        orchestration_system.delete()

        return "Orchestration system deleted"
