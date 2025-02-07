import typing
from typing import Optional
from .permission import Permission

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import Workspace

    User = get_user_model()


class PermissionChecker:
    @classmethod
    def check_create_permissions(cls, user: Optional["User"], workspace: "Workspace", resource_type: str):
        if not user:
            return False

        if workspace.owner == user or user.account_type in ["admin", "staff"]:
            return True

        permissions = Permission.objects.filter(
            role__collaborator_assignments__user=user,
            role__collaborator_assignments__workspace=workspace,
            resource_type__in=["*", resource_type]
        ).values_list("permission_type", flat=True)

        return any(perm in permissions for perm in ["*", "create"])

    @staticmethod
    def check_object_permissions(user: Optional["User"], workspace: "Workspace", resource_type: str):
        if not workspace:
            return ["view"]

        if user and (user == workspace.owner or user.account_type in ["admin", "staff"]):
            return ["view", "edit", "delete"]

        permissions = Permission.objects.exclude(
            permission_type="create"
        ).filter(
            role__collaborator_assignments__user=user,
            role__collaborator_assignments__workspace=workspace,
            resource_type__in=["*", resource_type]
        ).values_list("permission_type", flat=True)

        if not workspace.is_private and "view" not in list(permissions):
            permissions = list(permissions) + ["view"]

        return permissions
