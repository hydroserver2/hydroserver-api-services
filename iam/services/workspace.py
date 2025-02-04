import uuid
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import Workspace
from iam.schemas import WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody


User = get_user_model()


class WorkspaceService:
    @staticmethod
    def list(user: User, associated_only: bool):
        workspaces = Workspace.objects.visible(user=user)

        if associated_only:
            workspaces = workspaces.associated(user=user)

        return workspaces

    @staticmethod
    def get(user: User, uid: uuid.UUID):
        try:
            workspace = Workspace.objects.get(pk=uid)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        permissions = workspace.get_user_permissions(user=user)

        if "view" not in permissions and workspace.private is True:
            raise HttpError(404, "Workspace does not exist")

        if "view" not in permissions:
            raise HttpError(403, "You do not have permission to view this workspace")

        return workspace

    @staticmethod
    def create(user: User, data: WorkspacePostBody):
        if not Workspace.can_user_create(user):
            raise HttpError(403, "You do not have permission to create this workspace")

        return Workspace.objects.create(
            owner=user,
            **data.dict()
        )

    @staticmethod
    def update(user: User, uid: uuid.UUID, data: WorkspacePatchBody):
        workspace = Workspace.objects.get(pk=uid)

        permissions = workspace.get_user_permissions(user=user)

        if "view" not in permissions and "edit" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if "edit" not in permissions:
            raise HttpError(403, "You do not have permission to edit this workspace")

        workspace_body = data.dict(exclude_unset=True)

        for field, value in workspace_body.items():
            setattr(workspace, field, value)

        workspace.save()

        return workspace

    @staticmethod
    def delete(user: User, uid: uuid.UUID):
        workspace = Workspace.objects.get(pk=uid)

        permissions = workspace.get_user_permissions(user=user)

        if "view" not in permissions and "delete" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if "delete" not in permissions:
            raise HttpError(403, "You do not have permission to delete this workspace")

        workspace.delete()

    @staticmethod
    def transfer(user: User, uid: uuid.UUID, data: WorkspaceTransferBody):
        workspace = Workspace.objects.get(pk=uid)

    @staticmethod
    def accept(user: User, uid: uuid.UUID):
        workspace = Workspace.objects.get(pk=uid)
