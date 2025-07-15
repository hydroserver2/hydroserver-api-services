import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from iam.schemas import APIKeyPostBody, APIKeyPatchBody
from iam.schemas.api_key import APIKeyOrderByFields
from api.service import ServiceUtils
from .role import RoleService

User = get_user_model()
role_service = RoleService()


class APIKeyService(ServiceUtils):
    def get_api_key_for_action(
        self,
        principal: User,
        workspace_id: uuid.UUID,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        try:
            api_key = APIKey.objects.get(workspace=workspace, pk=uid)
        except APIKey.DoesNotExist:
            raise HttpError(404, "API key does not exist")

        permissions = api_key.get_principal_permissions(principal=principal)

        if "view" not in permissions:
            raise HttpError(404, "API key does not exist")

        if action not in permissions:
            raise HttpError(403, f"You do not have permission to {action} this API key")

        return api_key

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        workspace_id: uuid.UUID,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        queryset = APIKey.objects.filter(workspace=workspace)

        for field in [
            "role_id",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset, order_by, list(get_args(APIKeyOrderByFields))
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(
        self,
        principal: Optional[User | APIKey],
        workspace_id: uuid.UUID,
        uid: uuid.UUID,
    ):
        return self.get_api_key_for_action(
            principal=principal, workspace_id=workspace_id, uid=uid, action="view"
        )

    def create(self, principal: User, workspace_id: uuid.UUID, data: APIKeyPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=workspace_id
        )

        if not APIKey.can_principal_create(principal=principal, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this API key")

        apikey_role = role_service.get(principal=principal, uid=data.role_id)

        if not apikey_role.is_apikey_role:
            raise HttpError(400, "Role not supported for API key assignment")

        api_key, raw_key = APIKey.objects.create_with_key(
            workspace=workspace, **data.dict()
        )
        api_key.key = raw_key

        return api_key

    def update(
        self,
        principal: User,
        workspace_id: uuid.UUID,
        uid: uuid.UUID,
        data: APIKeyPatchBody,
    ):
        api_key = self.get_api_key_for_action(
            principal=principal, workspace_id=workspace_id, uid=uid, action="edit"
        )
        api_key_body = data.dict(exclude_unset=True)

        if "role_id" in api_key_body:
            apikey_role = role_service.get(principal=principal, uid=data.role_id)

            if not apikey_role.is_apikey_role:
                raise HttpError(400, "Role not supported for API key assignment")

        for field, value in api_key_body.items():
            setattr(api_key, field, value)

        api_key.save()

        return api_key

    def delete(self, principal: User, workspace_id: uuid.UUID, uid: uuid.UUID):
        api_key = self.get_api_key_for_action(
            principal=principal, workspace_id=workspace_id, uid=uid, action="delete"
        )

        api_key.delete()

        return "API key deleted"

    def regenerate(self, principal: User, workspace_id: uuid.UUID, uid: uuid.UUID):
        api_key = self.get_api_key_for_action(
            principal=principal, workspace_id=workspace_id, uid=uid, action="edit"
        )

        raw_key = api_key.generate_key()
        api_key.key = raw_key

        return api_key
