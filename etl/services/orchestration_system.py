import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from etl.models import OrchestrationSystem
from etl.schemas import OrchestrationSystemPostBody, OrchestrationSystemPatchBody
from etl.schemas.orchestration_system import OrchestrationSystemFields, OrchestrationSystemOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class OrchestrationSystemService(ServiceUtils):
    @staticmethod
    def get_orchestration_system_for_action(
        principal: User | APIKey,
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

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = OrchestrationSystem.objects

        for field in [
            "workspace_id",
            "orchestration_system_type",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(OrchestrationSystemOrderByFields)),
                {
                    "type": "orchestration_system_type"
                }
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_orchestration_system_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: User | APIKey, data: OrchestrationSystemPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        ) if data.workspace_id else (None, None,)

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
        principal: User | APIKey,
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

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        orchestration_system = self.get_orchestration_system_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if orchestration_system.data_sources.exists():
            raise HttpError(
                409, "Orchestration system in use by one or more data sources"
            )

        orchestration_system.delete()

        return "Orchestration system deleted"
