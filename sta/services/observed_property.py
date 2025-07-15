import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import ObservedProperty, VariableType
from sta.schemas import ObservedPropertyPostBody, ObservedPropertyPatchBody
from sta.schemas.observed_property import (
    ObservedPropertyFields,
    ObservedPropertyOrderByFields,
)
from api.service import ServiceUtils

User = get_user_model()


class ObservedPropertyService(ServiceUtils):
    @staticmethod
    def get_observed_property_for_action(
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            observed_property = ObservedProperty.objects.select_related(
                "workspace"
            ).get(pk=uid)
        except ObservedProperty.DoesNotExist:
            raise HttpError(404, "Observed property does not exist")

        observed_property_permissions = observed_property.get_principal_permissions(
            principal=principal
        )

        if "view" not in observed_property_permissions:
            raise HttpError(404, "Observed property does not exist")

        if action not in observed_property_permissions:
            raise HttpError(
                403, f"You do not have permission to {action} this observed property"
            )

        return observed_property

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = ObservedProperty.objects

        for field in [
            "workspace_id",
            "datastreams__thing_id",
            "datastreams__id",
            "observed_property_type",
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(ObservedPropertyOrderByFields)),
                {"type": "observed_property_type"},
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_observed_property_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: User | APIKey, data: ObservedPropertyPostBody):
        workspace, _ = (
            self.get_workspace(principal=principal, workspace_id=data.workspace_id)
            if data.workspace_id
            else (
                None,
                None,
            )
        )

        if not ObservedProperty.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this observed property"
            )

        observed_property = ObservedProperty.objects.create(
            workspace=workspace,
            **data.dict(include=set(ObservedPropertyFields.model_fields.keys())),
        )

        return observed_property

    def update(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        data: ObservedPropertyPatchBody,
    ):
        observed_property = self.get_observed_property_for_action(
            principal=principal, uid=uid, action="edit"
        )
        observed_property_data = data.dict(
            include=set(ObservedPropertyFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in observed_property_data.items():
            setattr(observed_property, field, value)

        observed_property.save()

        return observed_property

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        observed_property = self.get_observed_property_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if observed_property.datastreams.exists():
            raise HttpError(409, "Observed property in use by one or more datastreams")

        observed_property.delete()

        return "Observed property deleted"

    def list_variable_types(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False,
    ):
        queryset = VariableType.objects.order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list("name", flat=True)
