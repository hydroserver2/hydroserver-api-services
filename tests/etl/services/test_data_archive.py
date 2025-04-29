import pytest
from uuid import UUID
from iam.models import Workspace
from etl.services import DataArchiveService
from etl.schemas import (
    DataArchivePostBody,
    DataArchivePatchBody,
    DataArchiveGetResponse,
    OrchestrationSystemGetResponse,
)
from tests.utils import test_service_method

data_archive_service = DataArchiveService()


@pytest.mark.parametrize(
    "user, workspace, etl_system, length, max_queries",
    [
        ("admin", None, None, 3, 4),
        ("admin", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, 0, 2),
        ("admin", None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("owner", None, None, 3, 4),
        ("owner", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, 0, 2),
        ("owner", None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("editor", None, None, 3, 4),
        ("editor", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, 0, 2),
        ("editor", None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("viewer", None, None, 3, 4),
        ("viewer", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, 0, 2),
        ("viewer", None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("anonymous", None, None, 0, 4),
        ("anonymous", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, 0, 2),
        ("anonymous", None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        (None, None, None, 0, 4),
        (None, UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, 0, 2),
        (None, None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
    ],
)
def test_list_data_archive(
    django_assert_max_num_queries,
    get_user,
    user,
    workspace,
    etl_system,
    length,
    max_queries,
):
    with django_assert_max_num_queries(max_queries):
        with test_service_method(
            schema=DataArchiveGetResponse, response=length
        ) as context:
            context["result"] = data_archive_service.list(
                user=get_user(user),
                workspace_id=workspace if workspace else None,
                orchestration_system_id=etl_system if etl_system else None,
            )


@pytest.mark.parametrize(
    "user, data_archive, action, response, error_code",
    [
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "view",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "edit",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "delete",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            "view",
            "Data archive does not exist",
            404,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            "edit",
            "Data archive does not exist",
            404,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            "delete",
            "Data archive does not exist",
            404,
        ),
        (
            "owner",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "view",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "owner",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "edit",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "owner",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "delete",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "editor",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "view",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "editor",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "edit",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "editor",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "delete",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "viewer",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "view",
            {"name": "Test Data Archive"},
            None,
        ),
        (
            "viewer",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "edit",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "delete",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "view",
            "Data archive does not exist",
            404,
        ),
        (
            "anonymous",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "edit",
            "Data archive does not exist",
            404,
        ),
        (
            "anonymous",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "delete",
            "Data archive does not exist",
            404,
        ),
        (
            None,
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "view",
            "Data archive does not exist",
            404,
        ),
        (
            None,
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "edit",
            "Data archive does not exist",
            404,
        ),
        (
            None,
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "delete",
            "Data archive does not exist",
            404,
        ),
    ],
)
def test_get_data_archive_for_action(
    get_user, user, data_archive, action, response, error_code
):
    with test_service_method(
        schema=DataArchiveGetResponse, response=response, error_code=error_code
    ) as context:
        context["result"] = data_archive_service.get_data_archive_for_action(
            user=get_user(user), uid=data_archive, action=action
        )


@pytest.mark.parametrize(
    "user, orchestration_system, workspace, response, error_code",
    [
        (
            "owner",
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
            {"name": "Global Orchestration System"},
            None,
        ),
        (
            "owner",
            UUID("7cb900d2-eb11-4a59-a05b-dd02d95af312"),
            UUID("b27c51a0-7374-462d-8a53-d97d47176c10"),
            {"name": "Workspace Orchestration System"},
            None,
        ),
        (
            "owner",
            UUID("7cb900d2-eb11-4a59-a05b-dd02d95af312"),
            UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
            "The given orchestration system cannot",
            400,
        ),
    ],
)
def test_validate_orchestration_system(
    get_user, user, orchestration_system, workspace, response, error_code
):
    with test_service_method(
        schema=OrchestrationSystemGetResponse, response=response, error_code=error_code
    ) as context:
        workspace = Workspace.objects.get(pk=workspace)
        context["result"] = data_archive_service.validate_orchestration_system(
            user=get_user(user),
            orchestration_system_id=orchestration_system,
            workspace=workspace,
        )


@pytest.mark.parametrize(
    "crontab, interval, interval_units, response, error_code",
    [
        (
            "* * * * *",
            None,
            None,
            None,
            None,
        ),
        (
            None,
            5,
            "minutes",
            None,
            None,
        ),
        (
            "* * * * *",
            5,
            "minutes",
            "Only one of",
            400,
        ),
        (
            "* * * * *",
            5,
            None,
            "Only one of",
            400,
        ),
        (
            "* * * * *",
            None,
            "minutes",
            "Only one of",
            400,
        ),
        (
            "invalid",
            None,
            None,
            "Invalid crontab schedule",
            400,
        ),
        (
            None,
            5,
            None,
            "Both interval and interval units",
            400,
        ),
        (
            None,
            None,
            "minutes",
            "Both interval and interval units",
            400,
        ),
    ],
)
def test_validate_scheduling(crontab, interval, interval_units, response, error_code):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_archive_service.validate_scheduling(
            interval=interval,
            interval_units=interval_units,
            crontab=crontab,
        )


@pytest.mark.parametrize(
    "user, data, response, error_code",
    [
        (
            "admin",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "owner",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "editor",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "viewer",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
        (
            None,
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
    ],
)
def test_create_data_archive(get_user, user, data, response, error_code):
    data_archive_body = DataArchivePostBody(
        name=data["name"],
        workspace_id=data["workspace_id"],
        orchestration_system_id=data["orchestration_system_id"],
    )
    with test_service_method(
        schema=DataArchiveGetResponse,
        response=response or data,
        error_code=error_code,
        fields=(
            "name",
            "workspace_id",
        ),
    ) as context:
        context["result"] = data_archive_service.create(
            user=get_user(user), data=data_archive_body
        )


@pytest.mark.parametrize(
    "user, data_archive, data, response, error_code",
    [
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "owner",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "editor",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "viewer",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "Data archive does not exist",
            404,
        ),
        (
            None,
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "Data archive does not exist",
            404,
        ),
    ],
)
def test_update_data_archive(get_user, user, data_archive, data, response, error_code):
    data_archive_body = DataArchivePatchBody(
        name=data["name"], orchestration_system_id=data["orchestration_system_id"]
    )
    with test_service_method(
        schema=DataArchiveGetResponse,
        response=response or data,
        error_code=error_code,
        fields=("name",),
    ) as context:
        context["result"] = data_archive_service.update(
            user=get_user(user), uid=data_archive, data=data_archive_body
        )


@pytest.mark.parametrize(
    "user, data_archive, response, error_code",
    [
        ("admin", UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"), None, None),
        ("owner", UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"), None, None),
        ("editor", UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"), None, None),
        (
            "viewer",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "Data archive does not exist",
            404,
        ),
        (
            None,
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            "Data archive does not exist",
            404,
        ),
    ],
)
def test_delete_data_archive(get_user, user, data_archive, response, error_code):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_archive_service.delete(
            user=get_user(user),
            uid=data_archive,
        )


@pytest.mark.parametrize(
    "user, data_archive, datastream, response, error_code",
    [
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            UUID("e0506cac-3e50-4d0a-814d-7ae0146705b2"),
            None,
            None,
        ),
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "Datastream has already been linked",
            400,
        ),
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            UUID("9f96957b-ee20-4c7b-bf2b-673a0cda3a04"),
            "The datastream must share a workspace",
            400,
        ),
    ],
)
def test_link_datastream(
    get_user, user, data_archive, datastream, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_archive_service.link_datastream(
            user=get_user(user),
            uid=data_archive,
            datastream_id=datastream,
        )


@pytest.mark.parametrize(
    "user, data_archive, datastream, response, error_code",
    [
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            None,
            None,
        ),
        (
            "admin",
            UUID("6ff5de63-753b-458e-9735-e1ea68f9816c"),
            UUID("e0506cac-3e50-4d0a-814d-7ae0146705b2"),
            "The given data archive is not configured",
            400,
        ),
    ],
)
def test_unlink_datastream(
    get_user, user, data_archive, datastream, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_archive_service.unlink_datastream(
            user=get_user(user), uid=data_archive, datastream_id=datastream
        )
