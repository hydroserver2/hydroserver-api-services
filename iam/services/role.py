import uuid
from typing import Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.db.models import Q
from iam.models import Role, APIKey
from .utils import ServiceUtils

User = get_user_model()


class RoleService(ServiceUtils):
    def list(self, principal: Union[User, APIKey], workspace_id: uuid.UUID):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        return (
            Role.objects.filter(Q(workspace__isnull=True) | Q(workspace=workspace))
            .visible(principal=principal)
            .distinct()
        )

    def get(
        self, principal: Union[User, APIKey], uid: uuid.UUID, workspace_id: uuid.UUID
    ):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        try:
            role = Role.objects.get(
                Q(workspace=workspace) | Q(workspace__isnull=True), pk=uid
            )
        except Role.DoesNotExist:
            raise HttpError(404, "Role does not exist in workspace")

        role_permissions = role.get_principal_permissions(principal=principal)

        if "view" not in role_permissions:
            raise HttpError(404, "Role does not exist in workspace")

        return role
