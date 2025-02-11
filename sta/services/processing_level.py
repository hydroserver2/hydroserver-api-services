import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.models import ProcessingLevel
from sta.schemas import ProcessingLevelPostBody, ProcessingLevelPatchBody
from sta.schemas.processing_level import ProcessingLevelFields

User = get_user_model()


class ProcessingLevelService(ServiceUtils):
    @staticmethod
    def get_processing_level_for_action(user: User, uid: uuid.UUID, action: Literal["view", "edit", "delete"]):
        try:
            processing_level = ProcessingLevel.objects.select_related("workspace").get(pk=uid)
        except ProcessingLevel.DoesNotExist:
            raise HttpError(404, "Processing level does not exist")

        processing_level_permissions = processing_level.get_user_permissions(user=user)

        if "view" not in processing_level_permissions:
            raise HttpError(404, "Processing level does not exist")

        if action not in processing_level_permissions:
            raise HttpError(403, f"You do not have permission to {action} this processing level")

        return processing_level

    @staticmethod
    def list(user: Optional[User], workspace_id: Optional[uuid.UUID]):
        queryset = ProcessingLevel.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(user=user).distinct()

    def get(self, user: Optional[User], uid: uuid.UUID):
        return self.get_processing_level_for_action(user=user, uid=uid, action="view")

    def create(self, user: User, data: ProcessingLevelPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not ProcessingLevel.can_user_create(user=user, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this processing level")

        processing_level = ProcessingLevel.objects.create(
            workspace=workspace,
            **data.dict(include=set(ProcessingLevelFields.model_fields.keys()))
        )

        return processing_level

    def update(self, user: User, uid: uuid.UUID, data: ProcessingLevelPatchBody):
        processing_level = self.get_processing_level_for_action(user=user, uid=uid, action="edit")
        processing_level_data = data.dict(include=set(ProcessingLevelFields.model_fields.keys()), exclude_unset=True)

        for field, value in processing_level_data.items():
            setattr(processing_level, field, value)

        processing_level.save()

        return processing_level

    def delete(self, user: User, uid: uuid.UUID):
        processing_level = self.get_processing_level_for_action(user=user, uid=uid, action="delete")
        processing_level.delete()

        return "Processing level deleted"
