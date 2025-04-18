import uuid
from typing import Optional
from ninja.errors import HttpError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from iam.models import Workspace, WorkspaceTransferConfirmation
from iam.schemas import WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody
from .utils import ServiceUtils

User = get_user_model()


class WorkspaceService(ServiceUtils):
    @staticmethod
    def attach_role_and_transfer_fields(workspace: Workspace, user: Optional[User]):
        if not user:
            return workspace

        if workspace.transfer_details and (
            workspace.transfer_details.new_owner == user or workspace.owner == user
        ):
            workspace.pending_transfer_to = workspace.transfer_details.new_owner

        collaborator = next(
            (
                i
                for i in user.collaborator_roles
                if i.user == user and i.workspace == workspace
            ),
            None,
        )

        if collaborator:
            workspace.collaborator_role = collaborator.role

        return workspace

    def list(self, user: Optional[User], associated_only: bool = False):
        workspaces = Workspace.objects.visible(user=user).distinct()

        if user:
            user.collaborator_roles = list(user.workspace_roles.all())

        if associated_only:
            workspaces = workspaces.associated(user=user)

        workspaces = [
            self.attach_role_and_transfer_fields(workspace, user)
            for workspace in workspaces
        ]

        return workspaces

    def get(self, user: Optional[User], uid: uuid.UUID):
        workspace, _ = self.get_workspace(user=user, workspace_id=uid)

        if user:
            user.collaborator_roles = list(user.workspace_roles.all())

        workspace = self.attach_role_and_transfer_fields(workspace, user)

        return workspace

    @staticmethod
    def create(user: User, data: WorkspacePostBody):
        if not Workspace.can_user_create(user):
            raise HttpError(403, "You do not have permission to create this workspace")

        try:
            workspace = Workspace.objects.create(owner=user, **data.dict())
        except IntegrityError:
            raise HttpError(409, "Workspace name conflicts with an owned workspace")

        return workspace

    def update(self, user: User, uid: uuid.UUID, data: WorkspacePatchBody):
        workspace, permissions = self.get_workspace(user=user, workspace_id=uid)

        if "edit" not in permissions:
            raise HttpError(403, "You do not have permission to edit this workspace")

        workspace_body = data.dict(exclude_unset=True)

        for field, value in workspace_body.items():
            setattr(workspace, field, value)

        try:
            workspace.save()
        except IntegrityError:
            raise HttpError(409, "Workspace name conflicts with an owned workspace")

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
            raise HttpError(
                403, "You do not have permission to transfer this workspace"
            )

        if workspace.transfer_details:
            raise HttpError(400, "Workspace transfer is already pending")

        try:
            new_owner = User.objects.get(email=data.new_owner)
        except User.DoesNotExist:
            raise HttpError(400, f"No account with email '{data.new_owner}' found")

        if not Workspace.can_user_create(new_owner):
            raise HttpError(
                400, f"Workspace cannot be transferred to user '{data.new_owner}'"
            )

        if workspace.owner == new_owner:
            raise HttpError(400, f"Workspace already owned by user '{data.new_owner}'")

        WorkspaceTransferConfirmation.objects.create(
            workspace=workspace, new_owner=new_owner, initiated=timezone.now()
        )

        return "Workspace transfer initiated"

    def accept_transfer(self, user: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(
            user=user, workspace_id=uid, override_view_permissions=True
        )

        if "view" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if not workspace.transfer_details:
            raise HttpError(400, "No workspace transfer is pending")

        if workspace.transfer_details.new_owner != user:
            raise HttpError(
                403, "You do not have permission to accept this workspace transfer"
            )

        workspace.owner = user

        try:
            workspace.save()
        except IntegrityError:
            raise HttpError(409, "Workspace name conflicts with an owned workspace")

        workspace.transfer_details.delete()

        return "Workspace transfer accepted"

    def reject_transfer(self, user: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(
            user=user, workspace_id=uid, override_view_permissions=True
        )

        if "view" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if not workspace.transfer_details:
            raise HttpError(400, "No workspace transfer is pending")

        if not (
            workspace.transfer_details.new_owner == user or workspace.owner == user
        ):
            raise HttpError(
                403, "You do not have permission to reject this workspace transfer"
            )

        workspace.transfer_details.delete()

        return "Workspace transfer rejected"
