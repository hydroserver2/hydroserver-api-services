import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import ResultQualifier
from sta.schemas import ResultQualifierPostBody, ResultQualifierPatchBody
from sta.schemas.result_qualifier import ResultQualifierFields, ResultQualifierOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class ResultQualifierService(ServiceUtils):
    @staticmethod
    def get_result_qualifier_for_action(
        principal: User | APIKey,
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

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = ResultQualifier.objects

        for field in ["workspace_id"]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(ResultQualifierOrderByFields)),
            )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_result_qualifier_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: User | APIKey, data: ResultQualifierPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        ) if data.workspace_id else (None, None,)

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
        principal: User | APIKey,
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

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        result_qualifier = self.get_result_qualifier_for_action(
            principal=principal, uid=uid, action="delete"
        )
        result_qualifier.delete()

        return "Result qualifier deleted"
