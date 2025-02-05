import uuid
from ninja.errors import HttpError
from django.utils import timezone
from django.contrib.auth import get_user_model
from iam.models import Workspace, WorkspaceTransferConfirmation
from iam.schemas import WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody
from .utils import ServiceUtils


User = get_user_model()


class WorkspaceService(ServiceUtils):
    @staticmethod
    def list(user: User, associated_only: bool):
        workspaces = Workspace.objects.visible(user=user)

        if associated_only:
            workspaces = workspaces.associated(user=user)

        return workspaces

    def get(self, user: User, uid: uuid.UUID):
        workspace, _ = self.get_workspace(user=user, workspace_id=uid)

        return workspace

    @staticmethod
    def create(user: User, data: WorkspacePostBody):
        if not Workspace.can_user_create(user):
            raise HttpError(403, "You do not have permission to create this workspace")

        return Workspace.objects.create(
            owner=user,
            **data.dict()
        )

    def update(self, user: User, uid: uuid.UUID, data: WorkspacePatchBody):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid)

        if "edit" not in permissions:
            raise HttpError(403, "You do not have permission to edit this workspace")

        workspace_body = data.dict(exclude_unset=True)

        for field, value in workspace_body.items():
            setattr(workspace, field, value)

        workspace.save()

        return workspace

    def delete(self, user: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid)

        if "delete" not in permissions:
            raise HttpError(403, "You do not have permission to delete this workspace")

        workspace.delete()

    def transfer(self, user: User, uid: uuid.UUID, data: WorkspaceTransferBody):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid)

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

    def accept_transfer(self, user: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid, override_view_permissions=True)

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

    def reject_transfer(self, user: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid, override_view_permissions=True)

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
