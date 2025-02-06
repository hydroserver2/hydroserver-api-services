import uuid
from typing import Optional
from ninja.errors import HttpError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from iam.models import Workspace, WorkspaceTransferConfirmation
from iam.schemas import WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody
from .utils import ServiceUtils

User = get_user_model()


class WorkspaceService(ServiceUtils):
    @staticmethod
    def attach_role_and_transfer_fields(workspace: Workspace, user: Optional[User]):
        if not user:
            return workspace

        try:
            workspace_transfer = workspace.transfer_confirmation
        except ObjectDoesNotExist:
            workspace_transfer = None

        if workspace_transfer and (workspace_transfer.new_owner == user or workspace.owner == user):
            workspace.pending_transfer_to = workspace_transfer.new_owner

        collaborator = next((i for i in user.collaborator_roles if i.user == user and i.workspace == workspace), None)

        if collaborator:
            workspace.collaborator_role = collaborator.role

        return workspace

    def list(self, user: Optional[User], associated_only: bool = False):
        workspaces = Workspace.objects.select_related("transfer_confirmation").visible(user=user).distinct()

        if user:
            user.collaborator_roles = list(user.workspace_roles.all())

        if associated_only:
            workspaces = workspaces.associated(user=user)

        workspaces = [self.attach_role_and_transfer_fields(workspace, user) for workspace in workspaces]

        return workspaces

    def get(self, user: Optional[User], uid: uuid.UUID):
        workspace, _ = self.get_workspace(user=user, workspace_id=uid)
        user.collaborator_roles = list(user.workspace_roles.all()) if user else []
        workspace = self.attach_role_and_transfer_fields(workspace, user)

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

        user.collaborator_roles = list(user.workspace_roles.all())
        workspace = self.attach_role_and_transfer_fields(workspace, user)

        return workspace

    def delete(self, user: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid)

        if "delete" not in permissions:
            raise HttpError(403, "You do not have permission to delete this workspace")

        workspace.delete()

        return "Workspace deleted"

    def transfer(self, user: User, uid: uuid.UUID, data: WorkspaceTransferBody):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid)

        if "edit" not in permissions:
            raise HttpError(403, "You do not have permission to transfer this workspace")

        try:
            _ = workspace.transfer_confirmation
            raise HttpError(400, "Workspace transfer is already pending")
        except ObjectDoesNotExist:
            pass

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
