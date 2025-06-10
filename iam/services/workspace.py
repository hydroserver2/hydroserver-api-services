import uuid
from typing import Optional, Union
from ninja.errors import HttpError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from iam.models import Workspace, WorkspaceTransferConfirmation, APIKey
from iam.schemas import WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody
from hydroserver.service import ServiceUtils

User = get_user_model()


class WorkspaceService(ServiceUtils):
    @staticmethod
    def attach_role_and_transfer_fields(
        workspace: Workspace, principal: Optional[Union[User, APIKey]]
    ):
        if not principal:
            return workspace

        if workspace.transfer_details and (
            workspace.transfer_details.new_owner == principal
            or workspace.owner == principal
        ):
            workspace.pending_transfer_to = workspace.transfer_details.new_owner

        if hasattr(principal, "collaborator_roles"):
            collaborator = next(
                (
                    i
                    for i in principal.collaborator_roles
                    if i.user == principal and i.workspace == workspace
                ),
                None,
            )

            if collaborator:
                workspace.collaborator_role = collaborator.role

        return workspace

    def list(
        self, principal: Optional[Union[User, APIKey]], associated_only: bool = False
    ):
        workspaces = Workspace.objects.visible(principal=principal).distinct()

        if isinstance(principal, User):
            principal.collaborator_roles = list(principal.workspace_roles.all())

        if associated_only:
            workspaces = workspaces.associated(principal=principal)

        workspaces = [
            self.attach_role_and_transfer_fields(workspace, principal)
            for workspace in workspaces
        ]

        return workspaces

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        workspace, _ = self.get_workspace(principal=principal, workspace_id=uid)

        if isinstance(principal, User):
            principal.collaborator_roles = list(principal.workspace_roles.all())

        workspace = self.attach_role_and_transfer_fields(workspace, principal)

        return workspace

    @staticmethod
    def create(principal: User, data: WorkspacePostBody):
        if not Workspace.can_principal_create(principal):
            raise HttpError(403, "You do not have permission to create this workspace")

        try:
            workspace = Workspace.objects.create(owner=principal, **data.dict())
        except IntegrityError:
            raise HttpError(409, "Workspace name conflicts with an owned workspace")

        return workspace

    def update(self, principal: User, uid: uuid.UUID, data: WorkspacePatchBody):
        workspace, permissions = self.get_workspace(
            principal=principal, workspace_id=uid
        )

        if "edit" not in permissions:
            raise HttpError(403, "You do not have permission to edit this workspace")

        workspace_body = data.dict(exclude_unset=True)

        for field, value in workspace_body.items():
            setattr(workspace, field, value)

        try:
            workspace.save()
        except IntegrityError:
            raise HttpError(409, "Workspace name conflicts with an owned workspace")

        principal.collaborator_roles = list(principal.workspace_roles.all())
        workspace = self.attach_role_and_transfer_fields(workspace, principal)

        return workspace

    def delete(self, principal: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(
            principal=principal, workspace_id=uid
        )

        if "delete" not in permissions:
            raise HttpError(403, "You do not have permission to delete this workspace")

        workspace.delete()

        return "Workspace deleted"

    def transfer(self, principal: User, uid: uuid.UUID, data: WorkspaceTransferBody):
        workspace, permissions = self.get_workspace(
            principal=principal, workspace_id=uid
        )

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

        if not Workspace.can_principal_create(new_owner):
            raise HttpError(
                400, f"Workspace cannot be transferred to user '{data.new_owner}'"
            )

        if workspace.owner == new_owner:
            raise HttpError(400, f"Workspace already owned by user '{data.new_owner}'")

        WorkspaceTransferConfirmation.objects.create(
            workspace=workspace, new_owner=new_owner, initiated=timezone.now()
        )

        return "Workspace transfer initiated"

    def accept_transfer(self, principal: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(
            principal=principal, workspace_id=uid, override_view_permissions=True
        )

        if "view" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if not workspace.transfer_details:
            raise HttpError(400, "No workspace transfer is pending")

        if workspace.transfer_details.new_owner != principal:
            raise HttpError(
                403, "You do not have permission to accept this workspace transfer"
            )

        workspace.owner = principal

        try:
            workspace.save()
        except IntegrityError:
            raise HttpError(409, "Workspace name conflicts with an owned workspace")

        workspace.transfer_details.delete()

        return "Workspace transfer accepted"

    def reject_transfer(self, principal: User, uid: uuid.UUID):
        workspace, permissions = self.get_workspace(
            principal=principal, workspace_id=uid, override_view_permissions=True
        )

        if "view" not in permissions:
            raise HttpError(404, "Workspace does not exist")

        if not workspace.transfer_details:
            raise HttpError(400, "No workspace transfer is pending")

        if not (
            workspace.transfer_details.new_owner == principal
            or workspace.owner == principal
        ):
            raise HttpError(
                403, "You do not have permission to reject this workspace transfer"
            )

        workspace.transfer_details.delete()

        return "Workspace transfer rejected"
