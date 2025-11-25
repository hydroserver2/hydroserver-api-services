import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.http import HydroServerHttpRequest
from hydroserver.security import bearer_auth, session_auth, apikey_auth
from etl.services import JobService
from etl.schemas import JobSummaryResponse, JobDetailResponse, JobPostBody, JobPatchBody, JobQueryParameters


job_router = Router(tags=["ETL Jobs"])
job_service = JobService()


@job_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: list[JobSummaryResponse] | list[JobDetailResponse],
        401: str,
    },
    by_alias=True,
)
def get_jobs(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[JobQueryParameters],
):
    """
    Get ETL Jobs associated with the authenticated user.
    """

    return 200, job_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
        expand_related=query.expand_related,
    )


@job_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: JobDetailResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
def create_job(
    request: HydroServerHttpRequest,
    data: JobPostBody
):
    """
    Create a new ETL Job.
    """

    return 201, job_service.create(
        principal=request.principal, data=data
    )


@job_router.get(
    "/{job_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: JobSummaryResponse | JobDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_job(
    request: HydroServerHttpRequest,
    job_id: Path[uuid.UUID],
    expand_related: bool | None = None,
):
    """
    Get an ETL Job.
    """

    return 200, job_service.get(
        principal=request.principal, uid=job_id, expand_related=expand_related,
    )


@job_router.patch(
    "/{job_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: JobDetailResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_job(
    request: HydroServerHttpRequest,
    job_id: Path[uuid.UUID],
    data: JobPatchBody,
):
    """
    Update a ETL Job.
    """

    return 200, job_service.update(
        principal=request.principal,
        uid=job_id,
        data=data,
    )


@job_router.delete(
    "/{job_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: None,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_job(
    request: HydroServerHttpRequest,
    job_id: Path[uuid.UUID],
):
    """
    Delete an ETL Job.
    """

    return 204, job_service.delete(
        principal=request.principal, uid=job_id
    )
