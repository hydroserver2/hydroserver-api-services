import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import ObservedProperty
from sta.schemas import ObservedPropertyPostBody, ObservedPropertyPatchBody
from sta.schemas.observed_property import ObservedPropertyFields
from hydroserver.service import ServiceUtils

User = get_user_model()


class ObservedPropertyService(ServiceUtils):
    @staticmethod
    def get_observed_property_for_action(
        principal: Union[User, APIKey],
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

    @staticmethod
    def list(
        principal: Optional[Union[User, APIKey]], workspace_id: Optional[uuid.UUID]
    ):
        queryset = ObservedProperty.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(principal=principal).distinct()

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_observed_property_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: Union[User, APIKey], data: ObservedPropertyPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
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
        principal: Union[User, APIKey],
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

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        observed_property = self.get_observed_property_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if observed_property.datastreams.exists():
            raise HttpError(409, "Observed property in use by one or more datastreams")

        observed_property.delete()

        return "Observed property deleted"
