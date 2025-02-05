import uuid
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.db.models import Q
from iam.models import Role
from .utils import ServiceUtils


User = get_user_model()


class RoleService(ServiceUtils):
    def list(self, user: User, workspace_id: uuid.UUID):
        workspace, _ = self.get_workspace(user=user, workspace_id=workspace_id)

        return Role.objects.filter(
            Q(workspace__isnull=True) |
            Q(workspace=workspace)
        ).visible(user=user)

    def get(self, user: User, uid: uuid.UUID, workspace_id: uuid.UUID):
        workspace, _ = self.get_workspace(user=user, workspace_id=workspace_id)

        try:
            role = Role.objects.get(pk=uid, workspace=workspace)
        except Role.DoesNotExist:
            raise HttpError(404, "Role does not exist")

        role_permissions = role.get_user_permissions(user=user)

        if "view" not in role_permissions:
            raise HttpError(404, "Role does not exist")

        return role
