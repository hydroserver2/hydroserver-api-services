import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.models import ObservedProperty
from sta.schemas import ObservedPropertyPostBody, ObservedPropertyPatchBody
from sta.schemas.observed_property import ObservedPropertyFields

User = get_user_model()


class ObservedPropertyService(ServiceUtils):
    @staticmethod
    def get_observed_property_for_action(
        user: User, uid: uuid.UUID, action: Literal["view", "edit", "delete"]
    ):
        try:
            observed_property = ObservedProperty.objects.select_related(
                "workspace"
            ).get(pk=uid)
        except ObservedProperty.DoesNotExist:
            raise HttpError(404, "Observed property does not exist")

        observed_property_permissions = observed_property.get_user_permissions(
            user=user
        )

        if "view" not in observed_property_permissions:
            raise HttpError(404, "Observed property does not exist")

        if action not in observed_property_permissions:
            raise HttpError(
                403, f"You do not have permission to {action} this observed property"
            )

        return observed_property

    @staticmethod
    def list(user: Optional[User], workspace_id: Optional[uuid.UUID]):
        queryset = ObservedProperty.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(user=user).distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_observed_property_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: ObservedPropertyPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not ObservedProperty.can_user_create(user=user, workspace=workspace):
            raise HttpError(
                403, "You do not have permission to create this observed property"
            )

        observed_property = ObservedProperty.objects.create(
            workspace=workspace,
            **data.dict(include=set(ObservedPropertyFields.model_fields.keys())),
        )

        return observed_property

    def update(self, user: User, uid: uuid.UUID, data: ObservedPropertyPatchBody):
        observed_property = self.get_observed_property_for_action(
            user=user, uid=uid, action="edit"
        )
        observed_property_data = data.dict(
            include=set(ObservedPropertyFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in observed_property_data.items():
            setattr(observed_property, field, value)

        observed_property.save()

        return observed_property

    def delete(self, user: User, uid: uuid.UUID):
        observed_property = self.get_observed_property_for_action(
            user=user, uid=uid, action="delete"
        )

        if observed_property.datastreams.exists():
            raise HttpError(409, "Observed property in use by one or more datastreams")

        observed_property.delete()

        return "Observed property deleted"
