import pytest
import uuid
from collections import Counter
from ninja.errors import HttpError
from django.http import HttpResponse
from etl.services import JobService
from etl.schemas import (
    JobPostBody,
    JobPatchBody,
    JobSummaryResponse,
    JobDetailResponse
)

job_service = JobService()


@pytest.mark.parametrize(
    "principal, params, job_names, max_queries",
    [
        # Test user access
        (
            "owner",
            {},
            ["Test ETL Job"],
            4,
        ),
        (
            "editor",
            {},
            ["Test ETL Job"],
            4,
        ),
        (
            "viewer",
            {},
            ["Test ETL Job"],
            4,
        ),
        (
            "admin",
            {},
            ["Test ETL Job"],
            4,
        ),
        ("apikey", {}, [], 4),
        ("unaffiliated", {}, [], 4),
        ("anonymous", {}, [], 4),
        # Test pagination and order_by
        (
            "owner",
            {"page": 2, "page_size": 1, "order_by": "-name"},
            [],
            4,
        ),
        # Test filtering
        (
            "owner",
            {"job_type": "SDL"},
            ["Test ETL Job"],
            4,
        ),
    ],
)
def test_list_job(
    django_assert_max_num_queries,
    get_principal,
    principal,
    params,
    job_names,
    max_queries,
):
    with django_assert_max_num_queries(max_queries):
        http_response = HttpResponse()
        result = job_service.list(
            principal=get_principal(principal),
            response=http_response,
            page=params.pop("page", 1),
            page_size=params.pop("page_size", 100),
            order_by=[params.pop("order_by")] if "order_by" in params else [],
            filtering=params,
        )
        assert Counter(
            str(job.name) for job in result
        ) == Counter(job_names)
        assert (
            JobSummaryResponse.from_orm(job)
            for job in result
        )


@pytest.mark.parametrize(
    "principal, job, message, error_code",
    [
        (
            "owner",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "Test ETL Job",
            None,
        ),
        (
            "admin",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "Test ETL Job",
            None,
        ),
        (
            "editor",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "Test ETL Job",
            None,
        ),
        (
            "viewer",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "Test ETL Job",
            None,
        ),
        (
            "apikey",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "ETL Job does not exist",
            404,
        ),
    ],
)
def test_get_job(
    get_principal, principal, job, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            job_service.get(
                principal=get_principal(principal), uid=uuid.UUID(job)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        job_get = job_service.get(
            principal=get_principal(principal), uid=uuid.UUID(job)
        )
        assert job_get.name == message
        assert JobSummaryResponse.from_orm(job_get)


@pytest.mark.parametrize(
    "principal, workspace, message, error_code",
    [
        (
            "admin",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            None,
            None,
        ),
        (
            "admin",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            None,
            None,
        ),
        (
            "admin",
            "00000000-0000-0000-0000-000000000000",
            "Workspace does not exist",
            404,
        ),
        (
            "owner",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            None,
            None,
        ),
        (
            "owner",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            None,
            None,
        ),
        (
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            None,
            None,
        ),
        (
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            None,
            None,
        ),
        (
            "viewer",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            None,
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Workspace does not exist",
            404,
        ),
    ],
)
def test_create_job(
    get_principal, principal, workspace, message, error_code
):
    job_data = JobPostBody(
        name="New", workspace_id=uuid.UUID(workspace), job_type="Test", extractor=None, transformer=None, loader=None
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            job_service.create(
                principal=get_principal(principal), data=job_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        job_create = job_service.create(
            principal=get_principal(principal), data=job_data
        )
        assert job_create.name == job_data.name
        assert JobDetailResponse.from_orm(job_create)


@pytest.mark.parametrize(
    "principal, job, message, error_code",
    [
        ("admin", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("admin", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("owner", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("owner", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("editor", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("editor", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        (
            "viewer",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "apikey",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "ETL Job does not exist",
            404,
        ),
    ],
)
def test_edit_job(
    get_principal, principal, job, message, error_code
):
    job_data = JobPatchBody(
        name="New", job_type="Test"
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            job_service.update(
                principal=get_principal(principal),
                uid=uuid.UUID(job),
                data=job_data,
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        job_update = job_service.update(
            principal=get_principal(principal),
            uid=uuid.UUID(job),
            data=job_data,
        )
        assert job_update.name == job_data.name
        assert JobDetailResponse.from_orm(job_update)


@pytest.mark.parametrize(
    "principal, job, message, error_code",
    [
        ("admin", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("admin", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("owner", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("owner", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("editor", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        ("editor", "019adb5c-da8b-7970-877d-c3b4ca37cc60", None, None),
        (
            "viewer",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "apikey",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "019adb5c-da8b-7970-877d-c3b4ca37cc60",
            "ETL Job does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "ETL Job does not exist",
            404,
        ),
    ],
)
def test_delete_job(
    get_principal, principal, job, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            job_service.delete(
                principal=get_principal(principal), uid=uuid.UUID(job)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        job_delete = job_service.delete(
            principal=get_principal(principal), uid=uuid.UUID(job)
        )
        assert job_delete == "ETL Job deleted"
