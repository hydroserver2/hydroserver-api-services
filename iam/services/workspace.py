import uuid
from ninja.errors import HttpError
from django.utils import timezone
from django.contrib.auth import get_user_model
from iam.models import Workspace, WorkspaceTransferConfirmation
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
        try:
            workspace = Workspace.objects.get(pk=uid)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

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
        try:
            workspace = Workspace.objects.get(pk=uid)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        permissions = workspace.get_user_permissions(user=user)

        if "view" not in permissions and "delete" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if "delete" not in permissions:
            raise HttpError(403, "You do not have permission to delete this workspace")

        workspace.delete()

    @staticmethod
    def transfer(user: User, uid: uuid.UUID, data: WorkspaceTransferBody):
        try:
            workspace = Workspace.objects.get(pk=uid)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        permissions = workspace.get_user_permissions(user=user)

        if "view" not in permissions and "edit" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if "edit" not in permissions:
            raise HttpError(403, "You do not have permission to transfer this workspace")

        try:
            new_owner = User.objects.get(email=data.new_owner)
        except User.DoesNotExist:
            raise HttpError(400, f"No account with email '{data.new_owner}' found")

        if not Workspace.can_user_create(new_owner):
            raise HttpError(400, f"Workspace cannot be transferred to user '{data.new_owner}'")

        if workspace.owner == new_owner:
            raise HttpError(400, f"Workspace already owned by user '{data.new_owner}'")

        WorkspaceTransferConfirmation.objects.create(
            workspace=workspace,
            new_owner=new_owner,
            initiated=timezone.now()
        )

        return "Workspace transfer initiated"

    @staticmethod
    def accept_transfer(user: User, uid: uuid.UUID):
        try:
            workspace = Workspace.objects.select_related("transfer_confirmation").get(pk=uid)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        permissions = workspace.get_user_permissions(user=user)

        try:
            workspace_transfer_confirmation = workspace.transfer_confirmation
        except WorkspaceTransferConfirmation.DoesNotExist:
            if "view" not in permissions:
                raise HttpError(404, "Workspace does not exist")
            else:
                raise HttpError(400, "No workspace transfer is pending")

        if workspace_transfer_confirmation.new_owner != user:
            if "view" not in permissions:
                raise HttpError(404, "Workspace does not exist")
            else:
                raise HttpError(403, "You do not have permission to accept this workspace transfer")

        workspace.owner = user
        workspace_transfer_confirmation.delete()
        workspace.save()

        return "Workspace transfer accepted"

    @staticmethod
    def reject_transfer(user: User, uid: uuid.UUID):
        try:
            workspace = Workspace.objects.select_related("transfer_confirmation").get(pk=uid)
        except Workspace.DoesNotExist:
            raise HttpError(404, "Workspace does not exist")

        permissions = workspace.get_user_permissions(user=user)

        try:
            workspace_transfer_confirmation = workspace.transfer_confirmation
        except WorkspaceTransferConfirmation.DoesNotExist:
            if "view" not in permissions:
                raise HttpError(404, "Workspace does not exist")
            else:
                raise HttpError(400, "No workspace transfer is pending")

        if not (workspace_transfer_confirmation.new_owner == user or "edit" in permissions):
            if "view" not in permissions:
                raise HttpError(404, "Workspace does not exist")
            else:
                raise HttpError(403, "You do not have permission to reject this workspace transfer")

        workspace_transfer_confirmation.delete()

        return "Workspace transfer rejected"
