import uuid
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import Workspace

User = get_user_model()


class ServiceUtils:
    @staticmethod
    def get_workspace(user: User, workspace_id: uuid.UUID, override_view_permissions=False):
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        workspace_permissions = workspace.get_user_permissions(user=user)

        if "view" not in workspace_permissions and workspace.private is True and not override_view_permissions:
            raise HttpError(404, "Workspace does not exist")

        return workspace, workspace_permissions
