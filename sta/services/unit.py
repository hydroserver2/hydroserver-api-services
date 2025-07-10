import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import Unit, UnitType
from sta.schemas import UnitPostBody, UnitPatchBody
from sta.schemas.unit import UnitFields, UnitOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class UnitService(ServiceUtils):
    @staticmethod
    def get_unit_for_action(
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            unit = Unit.objects.select_related("workspace").get(pk=uid)
        except Unit.DoesNotExist:
            raise HttpError(404, "Unit does not exist")

        unit_permissions = unit.get_principal_permissions(principal=principal)

        if "view" not in unit_permissions:
            raise HttpError(404, "Unit does not exist")

        if action not in unit_permissions:
            raise HttpError(403, f"You do not have permission to {action} this unit")

        return unit

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = Unit.objects

        for field in [
            "workspace_id",
            "datastreams__thing_id",
            "datastreams__id",
            "unit_type",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(UnitOrderByFields)),
                {
                    "type": "unit_type"
                }
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_unit_for_action(principal=principal, uid=uid, action="view")

    def create(self, principal: User | APIKey, data: UnitPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        ) if data.workspace_id else (None, None,)

        if not Unit.can_principal_create(principal=principal, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this unit")

        unit = Unit.objects.create(
            workspace=workspace,
            **data.dict(include=set(UnitFields.model_fields.keys())),
        )

        return unit

    def update(
        self, principal: User | APIKey, uid: uuid.UUID, data: UnitPatchBody
    ):
        unit = self.get_unit_for_action(principal=principal, uid=uid, action="edit")
        unit_data = data.dict(
            include=set(UnitFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in unit_data.items():
            setattr(unit, field, value)

        unit.save()

        return unit

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        unit = self.get_unit_for_action(principal=principal, uid=uid, action="delete")

        if unit.datastreams.exists():
            raise HttpError(409, "Unit in use by one or more datastreams")

        unit.delete()

        return "Unit deleted"

    def list_unit_types(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False
    ):
        queryset = UnitType.objects.order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list(
            "name", flat=True
        )
