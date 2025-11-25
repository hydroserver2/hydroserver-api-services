import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from iam.models import APIKey
from etl.models import Job
from etl.schemas import (
    JobSummaryResponse,
    JobDetailResponse,
    JobPostBody,
    JobPatchBody,
)
from etl.schemas.job import (
    JobFields,
    JobOrderByFields,
)
from api.service import ServiceUtils

User = get_user_model()


class JobService(ServiceUtils):

    def get_job_for_action(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        expand_related: Optional[bool] = None,
        raise_400: bool = False,
    ):
        try:
            job = Job.objects
            if expand_related:
                job = self.select_expanded_fields(job)
            job = job.get(pk=uid)
        except Job.DoesNotExist:
            raise HttpError(
                404 if not raise_400 else 400, "ETL Job does not exist"
            )

        job_permissions = (
            job.get_principal_permissions(principal=principal)
        )

        if "view" not in job_permissions:
            raise HttpError(
                404 if not raise_400 else 400, "ETL Job does not exist"
            )

        if action not in job_permissions:
            raise HttpError(
                403 if not raise_400 else 400,
                f"You do not have permission to {action} this ETL job",
            )

        return job

    @staticmethod
    def select_expanded_fields(queryset: QuerySet) -> QuerySet:
        return queryset.select_related("workspace")

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
        expand_related: Optional[bool] = None,
    ):
        queryset = Job.objects

        for field in [
            "workspace_id",
            "job_type",
            "extractor_type",
            "transformer_type",
            "loader_type"
        ]:
            if field in filtering:
                queryset = self.apply_filters(queryset, field, filtering[field])

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(JobOrderByFields)),
                {"type": "job_type"},
            )

        if expand_related:
            queryset = self.select_expanded_fields(queryset)

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        return [
            (
                JobDetailResponse.model_validate(job)
                if expand_related
                else JobSummaryResponse.model_validate(
                    job
                )
            )
            for job in queryset.all()
        ]

    def get(
        self,
        principal: Optional[User | APIKey],
        uid: uuid.UUID,
        expand_related: Optional[bool] = None,
    ):
        job = self.get_job_for_action(
            principal=principal, uid=uid, action="view", expand_related=expand_related
        )

        return (
            JobDetailResponse.model_validate(job)
            if expand_related
            else JobSummaryResponse.model_validate(job)
        )

    def create(
        self,
        principal: User | APIKey,
        data: JobPostBody,
    ):
        workspace, _ = self.get_workspace(principal=principal, workspace_id=data.workspace_id)

        if not Job.can_principal_create(
            principal=principal, workspace=workspace
        ):
            raise HttpError(
                403, "You do not have permission to create this ETL job"
            )

        job = Job.objects.create(
            workspace=workspace,
            extractor_type=data.extractor.settings_type if data.extractor else None,
            extractor_settings=data.extractor.settings if data.extractor else None,
            transformer_type=data.transformer.settings_type if data.transformer else None,
            transformer_settings=data.transformer.settings if data.transformer else None,
            loader_type=data.loader.settings_type if data.loader else None,
            loader_settings=data.loader.settings if data.loader else None,
            **data.dict(include=set(JobFields.model_fields.keys())),
        )

        return self.get(
            principal=principal,
            uid=job.id,
            expand_related=True,
        )

    def update(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        data: JobPatchBody,
    ):
        job = self.get_job_for_action(
            principal=principal, uid=uid, action="edit"
        )
        job_data = data.dict(
            include=set(JobFields.model_fields.keys() | {"extractor", "transformer", "loader"}),
            exclude_unset=True,
        )

        for field, value in job_data.items():
            if field in ["extractor", "transformer", "loader"]:
                if "settings_type" in value:
                    setattr(job, f"{field}_type", value["settings_type"])
                if "settings" in value:
                    setattr(job, f"{field}_settings", value["settings"])
            else:
                setattr(job, field, value)

        job.save()

        return self.get(
            principal=principal,
            uid=job.id,
            expand_related=True,
        )

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        job = self.get_job_for_action(
            principal=principal, uid=uid, action="delete", expand_related=True
        )

        job.delete()

        return "ETL Job deleted"
