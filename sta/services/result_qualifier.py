import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import ResultQualifier
from sta.schemas import ResultQualifierPostBody, ResultQualifierPatchBody
from sta.schemas.result_qualifier import ResultQualifierFields
from hydroserver.service import ServiceUtils

User = get_user_model()


class ResultQualifierService(ServiceUtils):
    @staticmethod
    def get_result_qualifier_for_action(
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            result_qualifier = ResultQualifier.objects.select_related("workspace").get(
                pk=uid
            )
        except ResultQualifier.DoesNotExist:
            raise HttpError(404, "Result qualifier does not exist")

        result_qualifier_permissions = result_qualifier.get_principal_permissions(
            principal=principal
        )

        if "view" not in result_qualifier_permissions:
            raise HttpError(404, "Result qualifier does not exist")

        if action not in result_qualifier_permissions:
            raise HttpError(
                403, f"You do not have permission to {action} this result qualifier"
            )

        return result_qualifier

    @staticmethod
    def list(
        principal: Optional[Union[User, APIKey]], workspace_id: Optional[uuid.UUID]
    ):
        queryset = ResultQualifier.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(principal=principal).distinct()

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_result_qualifier_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: Union[User, APIKey], data: ResultQualifierPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not ResultQualifier.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this result qualifier"
            )

        result_qualifier = ResultQualifier.objects.create(
            workspace=workspace,
            **data.dict(include=set(ResultQualifierFields.model_fields.keys())),
        )

        return result_qualifier

    def update(
        self,
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        data: ResultQualifierPatchBody,
    ):
        result_qualifier = self.get_result_qualifier_for_action(
            principal=principal, uid=uid, action="edit"
        )
        result_qualifier_data = data.dict(
            include=set(ResultQualifierFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in result_qualifier_data.items():
            setattr(result_qualifier, field, value)

        result_qualifier.save()

        return result_qualifier

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        result_qualifier = self.get_result_qualifier_for_action(
            principal=principal, uid=uid, action="delete"
        )
        result_qualifier.delete()

        return "Result qualifier deleted"
