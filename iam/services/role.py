import uuid
from typing import Union, Optional
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from iam.models import Role, APIKey
from hydroserver.service import ServiceUtils

User = get_user_model()


class RoleService(ServiceUtils):
    def list(
        self,
        principal: Optional[Union[User, APIKey]],
        response: HttpResponse,
        workspace_id: uuid.UUID,
        page: int = 1,
        page_size: int = 100,
        ordering: Optional[str] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = Role.objects

        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        queryset = queryset.filter(Q(workspace__isnull=True) | Q(workspace=workspace))

        for field in [
            "is_user_role",
            "is_apikey_role",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        queryset = self.apply_ordering(
            queryset,
            ordering,
            [
                "name",
            ],
        )

        queryset = queryset.visible(principal=principal).prefetch_related(
            "permissions"
        ).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(
        self, principal: Union[User, APIKey], uid: uuid.UUID, workspace_id: uuid.UUID
    ):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        try:
            role = Role.objects.get(
                Q(workspace=workspace) | Q(workspace__isnull=True), pk=uid
            )
        except Role.DoesNotExist:
            raise HttpError(404, "Role does not exist in workspace")

        role_permissions = role.get_principal_permissions(principal=principal)

        if "view" not in role_permissions:
            raise HttpError(404, "Role does not exist in workspace")

        return role
