import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from iam.models import APIKey
from sta.models import ProcessingLevel
from sta.schemas import ProcessingLevelPostBody, ProcessingLevelPatchBody
from sta.schemas.processing_level import ProcessingLevelFields
from hydroserver.service import ServiceUtils

User = get_user_model()


class ProcessingLevelService(ServiceUtils):
    @staticmethod
    def get_processing_level_for_action(
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            processing_level = ProcessingLevel.objects.select_related("workspace").get(
                pk=uid
            )
        except ProcessingLevel.DoesNotExist:
            raise HttpError(404, "Processing level does not exist")

        processing_level_permissions = processing_level.get_principal_permissions(
            principal=principal
        )

        if "view" not in processing_level_permissions:
            raise HttpError(404, "Processing level does not exist")

        if action not in processing_level_permissions:
            raise HttpError(
                403, f"You do not have permission to {action} this processing level"
            )

        return processing_level

    def list(
        self,
        principal: Optional[Union[User, APIKey]],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        ordering: Optional[str] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = ProcessingLevel.objects

        for field in [
            "workspace_id",
            "thing_id",
            "datastream_id",
            "code",
        ]:
            if field in filtering:
                if field == "thing_id":
                    queryset = self.apply_filters(
                        queryset, f"datastreams__{field}", filtering[field]
                    )
                elif field == "datastream_id":
                    queryset = self.apply_filters(
                        queryset, f"datastreams__id", filtering[field]
                    )
                else:
                    queryset = self.apply_filters(queryset, field, filtering[field])

        queryset = self.apply_ordering(
            queryset,
            ordering,
            [
                "code",
            ],
        )

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_processing_level_for_action(
            principal=principal, uid=uid, action="view"
        )

    def create(self, principal: Union[User, APIKey], data: ProcessingLevelPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not ProcessingLevel.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this processing level"
            )

        processing_level = ProcessingLevel.objects.create(
            workspace=workspace,
            **data.dict(include=set(ProcessingLevelFields.model_fields.keys())),
        )

        return processing_level

    def update(
        self,
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        data: ProcessingLevelPatchBody,
    ):
        processing_level = self.get_processing_level_for_action(
            principal=principal, uid=uid, action="edit"
        )
        processing_level_data = data.dict(
            include=set(ProcessingLevelFields.model_fields.keys()), exclude_unset=True
        )

        for field, value in processing_level_data.items():
            setattr(processing_level, field, value)

        processing_level.save()

        return processing_level

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        processing_level = self.get_processing_level_for_action(
            principal=principal, uid=uid, action="delete"
        )

        if processing_level.datastreams.exists():
            raise HttpError(409, "Processing level in use by one or more datastreams")

        processing_level.delete()

        return "Processing level deleted"
