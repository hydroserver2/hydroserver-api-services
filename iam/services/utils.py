import uuid
from typing import Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import Workspace, APIKey

User = get_user_model()


class ServiceUtils:
    @staticmethod
    def get_workspace(
        principal: Union[User, APIKey],
        workspace_id: uuid.UUID,
        override_view_permissions=False,
    ):
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        workspace_permissions = workspace.get_principal_permissions(principal=principal)

        if (
            "view" not in workspace_permissions
            and workspace.is_private is True
            and not override_view_permissions
        ):
            raise HttpError(404, "Workspace does not exist")

        return workspace, workspace_permissions

    @staticmethod
    def handle_http_404_error(operation, *args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except HttpError as e:
            if e.status_code == 404:
                raise HttpError(400, str(e))
            else:
                raise e
