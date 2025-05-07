import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import APIKey
from iam.services.utils import ServiceUtils
from sta.models import Unit
from sta.schemas import UnitPostBody, UnitPatchBody
from sta.schemas.unit import UnitFields

User = get_user_model()


class UnitService(ServiceUtils):
    @staticmethod
    def get_unit_for_action(
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            unit = Unit.objects.select_related("workspace").get(pk=uid)
        except Unit.DoesNotExist:
            raise HttpError(404, "Unit does not exist")

        unit_permissions = unit.get_principal_permissions(principal=principal)

        if "view" not in unit_permissions:
            raise HttpError(404, "Unit does not exist")

        if action not in unit_permissions:
            raise HttpError(403, f"You do not have permission to {action} this unit")

        return unit

    @staticmethod
    def list(
        principal: Optional[Union[User, APIKey]], workspace_id: Optional[uuid.UUID]
    ):
        queryset = Unit.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(principal=principal).distinct()

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_unit_for_action(principal=principal, uid=uid, action="view")

    def create(self, principal: Union[User, APIKey], data: UnitPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not Unit.can_principal_create(principal=principal, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this unit")

        unit = Unit.objects.create(
            workspace=workspace,
            **data.dict(include=set(UnitFields.model_fields.keys())),
        )

        return unit

    def update(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: UnitPatchBody
    ):
        unit = self.get_unit_for_action(principal=principal, uid=uid, action="edit")
        unit_data = data.dict(
            include=set(UnitFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in unit_data.items():
            setattr(unit, field, value)

        unit.save()

        return unit

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        unit = self.get_unit_for_action(principal=principal, uid=uid, action="delete")

        if unit.datastreams.exists():
            raise HttpError(409, "Unit in use by one or more datastreams")

        unit.delete()

        return "Unit deleted"
