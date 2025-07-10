import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from iam.models import Role
from iam.schemas.role import RoleOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class RoleService(ServiceUtils):
    @staticmethod
    def get_role_for_action(
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            role = Role.objects.select_related("workspace").get(pk=uid)
        except Role.DoesNotExist:
            raise HttpError(404, "Role does not exist")

        role_permissions = role.get_principal_permissions(principal=principal)

        if "view" not in role_permissions:
            raise HttpError(404, "Role does not exist")

        if action not in role_permissions:
            raise HttpError(403, f"You do not have permission to {action} this role")

        return role

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = Role.objects

        for field in [
            "workspace_id",
            "is_user_role",
            "is_apikey_role",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(RoleOrderByFields)),
            )

        queryset = queryset.visible(principal=principal).prefetch_related(
            "permissions"
        ).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_role_for_action(principal=principal, uid=uid, action="view")
