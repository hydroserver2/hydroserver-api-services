import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.models import Unit
from sta.schemas import UnitPostBody, UnitPatchBody
from sta.schemas.unit import UnitFields

User = get_user_model()


class UnitService(ServiceUtils):
    @staticmethod
    def get_unit_for_action(user: User, uid: uuid.UUID, action: Literal["view", "edit", "delete"]):
        try:
            unit = Unit.objects.select_related("workspace").get(pk=uid)
        except Unit.DoesNotExist:
            raise HttpError(404, "Unit does not exist")

        unit_permissions = unit.get_user_permissions(user=user)

        if "view" not in unit_permissions:
            raise HttpError(404, "Unit does not exist")

        if action not in unit_permissions:
            raise HttpError(403, f"You do not have permission to {action} this unit")

        return unit

    @staticmethod
    def list(user: Optional[User], workspace_id: Optional[uuid.UUID]):
        queryset = Unit.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(user=user).distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_unit_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: UnitPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not Unit.can_user_create(user=user, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this unit")

        unit = Unit.objects.create(
            workspace=workspace,
            **data.dict(include=set(UnitFields.model_fields.keys()))
        )

        return unit

    def update(self, user: User, uid: uuid.UUID, data: UnitPatchBody):
        unit = self.get_unit_for_action(user=user, uid=uid, action="edit")
        unit_data = data.dict(include=set(UnitFields.model_fields.keys()), exclude_unset=True)

        for field, value in unit_data.items():
            setattr(unit, field, value)

        unit.save()

        return unit

    def delete(self, user: User, uid: uuid.UUID):
        unit = self.get_unit_for_action(user=user, uid=uid, action="delete")
        unit.delete()

        return "Unit deleted"
