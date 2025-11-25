import uuid
from typing import Any, Literal
from ninja import Schema, Field, Query
from api.schemas import BaseGetResponse, BasePostBody, BasePatchBody, CollectionQueryParameters
from iam.schemas import WorkspaceSummaryResponse


_order_by_fields = (
    "name", "type", "extractorType", "transformerType", "loaderType"
)

JobOrderByFields = Literal[
    *_order_by_fields, *[f"-{f}" for f in _order_by_fields]
]


class JobQueryParameters(CollectionQueryParameters):
    order_by: list[JobOrderByFields] | None = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID] = Query([], description="Filter by workspace ID.")
    job_type: list[str] = Query(
        [], description="Filters by the type of the job.", alias="type"
    )
    extractor_type: list[str | Literal["null"]] = Query(
        [], description="Filters by the extractor type of the job.",
    )
    transformer_type: list[str | Literal["null"]] = Query(
        [], description="Filters by the transformer type of the job.",
    )
    loader_type: list[str | Literal["null"]] = Query(
        [], description="Filters by the loader type of the job.",
    )
    expand_related: bool | None = None


class JobSettingsFields(Schema):
    settings_type: str = Field(..., alias="type")
    settings: dict[str, Any]


class JobSettingsResponse(BaseGetResponse, JobSettingsFields):
    pass


class JobSettingsPostBody(BasePostBody, JobSettingsFields):
    pass


class JobSettingsPatchBody(BasePatchBody, JobSettingsFields):
    pass


class JobFields(Schema):
    name: str
    job_type: str = Field(..., alias="type")


class JobSummaryResponse(BaseGetResponse, JobFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    extractor: JobSettingsResponse | None = None
    transformer: JobSettingsResponse | None = None
    loader: JobSettingsResponse | None = None


class JobDetailResponse(BaseGetResponse, JobFields):
    id: uuid.UUID
    workspace: WorkspaceSummaryResponse
    extractor: JobSettingsResponse | None = None
    transformer: JobSettingsResponse | None = None
    loader: JobSettingsResponse | None = None


class JobPostBody(BasePostBody, JobFields):
    workspace_id: uuid.UUID
    extractor: JobSettingsPostBody | None = None
    transformer: JobSettingsPostBody | None = None
    loader: JobSettingsPostBody | None = None


class JobPatchBody(BasePatchBody, JobFields):
    extractor: JobSettingsPatchBody | None = None
    transformer: JobSettingsPatchBody | None = None
    loader: JobSettingsPatchBody | None = None
