import typing
from .workspace import Workspace
from .permission import Permission

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class PermissionChecker:
    @classmethod
    def check_create_permissions(cls, user: "User", workspace: Workspace, resource_type: str):
        if workspace.owner == user or user.account_type in ["admin", "staff"]:
            return True

        permissions = Permission.objects.filter(
            role__collaborator_assignments__user_id=user.id,
            role__workspace_id=workspace.id,
            resource_type__in=["*", resource_type]
        ).values_list("permission_type", flat=True)

        return any(perm in permissions for perm in ["*", "create"])

    @staticmethod
    def check_object_permissions(user: "User", workspace: Workspace, resource_type: str):
        if not workspace:
            return ["view"]

        if user == workspace.owner or user.account_type in ["admin", "staff"]:
            return ["view", "edit", "delete"]

        permissions = Permission.objects.exclude(
            permission_type="create"
        ).filter(
            role__collaborator_assignments__user_id=user.id,
            role__workspace_id=workspace.id,
            resource_type__in=["*", resource_type]
        ).values_list("permission_type", flat=True)

        if not workspace.private and "view" not in permissions:
            permissions.append("view")

        return permissions
