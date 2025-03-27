import uuid
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import Collaborator
from iam.schemas import CollaboratorPostBody, CollaboratorDeleteBody
from .utils import ServiceUtils
from .role import RoleService

User = get_user_model()
role_service = RoleService()


class CollaboratorService(ServiceUtils):
    def list(self, user: User, workspace_id: uuid.UUID):
        workspace, _ = self.get_workspace(user=user, workspace_id=workspace_id)

        return (
            Collaborator.objects.filter(workspace=workspace)
            .visible(user=user)
            .distinct()
        )

    def create(self, user: User, workspace_id: uuid.UUID, data: CollaboratorPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=workspace_id)

        if not Collaborator.can_user_create(user=user, workspace=workspace):
            raise HttpError(403, "You do not have permission to add this collaborator")

        try:
            new_collaborator = User.objects.get(email=data.email)
        except User.DoesNotExist:
            raise HttpError(400, f"No account with email '{data.email}' found")

        workspace_collaborator_emails = (
            Collaborator.objects.filter(workspace=workspace)
            .select_related("user")
            .values_list("user__email", flat=True)
        )

        if new_collaborator.email in workspace_collaborator_emails:
            raise HttpError(
                400,
                f"Account with email '{data.email}' already collaborates on the workspace",
            )

        if new_collaborator.email == workspace.owner.email:
            raise HttpError(
                400, f"Account with email '{data.email}' already owns the workspace"
            )

        collaborator_role = role_service.get(
            user=user, workspace_id=workspace_id, uid=data.role_id
        )

        return Collaborator.objects.create(
            workspace=workspace, user=new_collaborator, role_id=collaborator_role.id
        )

    def update(self, user: User, workspace_id: uuid.UUID, data: CollaboratorPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=workspace_id)

        try:
            collaborator = Collaborator.objects.select_related("workspace").get(
                workspace=workspace, user__email=data.email
            )
        except Collaborator.DoesNotExist:
            raise HttpError(400, f"No collaborator with email '{data.email}' found")

        permissions = collaborator.get_user_permissions(user=user)

        if not any(permission in permissions for permission in ("*", "edit")):
            raise HttpError(
                403, f"You do not have permission to modify this collaborator's role"
            )

        collaborator.role = role_service.get(
            user=user, workspace_id=workspace_id, uid=data.role_id
        )
        collaborator.save()

        return collaborator

    def delete(self, user: User, workspace_id: uuid.UUID, data: CollaboratorDeleteBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=workspace_id)

        try:
            collaborator = Collaborator.objects.select_related("workspace", "user").get(
                workspace=workspace, user__email=data.email
            )
        except Collaborator.DoesNotExist:
            raise HttpError(400, f"No collaborator with email '{data.email}' found")

        permissions = collaborator.get_user_permissions(user=user)

        if (
            not any(permission in permissions for permission in ("*", "delete"))
            and user.email != collaborator.user.email
        ):
            raise HttpError(
                403, f"You do not have permission to remove this collaborator"
            )

        collaborator.delete()

        return "Collaborator removed from workspace"
