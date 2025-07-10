import pytest
from uuid import UUID
from collections import Counter
from django.http import HttpResponse
from iam.models import Workspace
from etl.services import DataSourceService
from etl.schemas import (
    DataSourcePostBody,
    DataSourcePatchBody,
    DataSourceDetailResponse,
    OrchestrationSystemDetailResponse,
)
from tests.utils import test_service_method

data_source_service = DataSourceService()


@pytest.mark.parametrize(
    "principal, params, data_source_names, max_queries",
    [
        # Test user access
        ("owner", {}, ["Test Data Source", "Crontab Data Source", "Interval Data Source"], 5),
        ("editor", {}, ["Test Data Source", "Crontab Data Source", "Interval Data Source"], 5),
        ("viewer", {}, ["Test Data Source", "Crontab Data Source", "Interval Data Source"], 5),
        ("admin", {}, ["Test Data Source", "Crontab Data Source", "Interval Data Source"], 5),
        ("apikey", {}, ["Test Data Source", "Crontab Data Source", "Interval Data Source"], 5),
        ("unaffiliated", {}, [], 5),
        ("anonymous", {}, [], 5),
        # Test pagination and order_by
        ("owner", {"page": 2, "page_size": 1, "order_by": "-name"}, ["Interval Data Source"], 5),
        # Test filtering
        ("owner", {"orchestration_system_id": "320ad0e1-1426-47f6-8a3a-886a7111a7c2"}, ["Test Data Source", "Crontab Data Source", "Interval Data Source"], 5),
    ],
)
def test_list_data_source(
    django_assert_max_num_queries,
    get_principal,
    principal,
    params,
    data_source_names,
    max_queries,
):
    with django_assert_max_num_queries(max_queries):
        http_response = HttpResponse()
        result = data_source_service.list(
            principal=get_principal(principal),
            response=http_response,
            page=params.pop("page", 1),
            page_size=params.pop("page_size", 100),
            order_by=[params.pop("order_by")] if "order_by" in params else [],
            filtering=params,
        )
        assert Counter(str(data_source.name) for data_source in result) == Counter(data_source_names)
        assert (DataSourceDetailResponse.from_orm(data_source) for data_source in result)


@pytest.mark.parametrize(
    "principal, data_source, action, response, error_code",
    [
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            "view",
            "Data source does not exist",
            404,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            "edit",
            "Data source does not exist",
            404,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            "delete",
            "Data source does not exist",
            404,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "apikey",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            {"name": "Test Data Source"},
            None,
        ),
        (
            "apikey",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            "Data source does not exist",
            404,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            "Data source does not exist",
            404,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            "Data source does not exist",
            404,
        ),
        (
            None,
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "view",
            "Data source does not exist",
            404,
        ),
        (
            None,
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "edit",
            "Data source does not exist",
            404,
        ),
        (
            None,
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "delete",
            "Data source does not exist",
            404,
        ),
    ],
)
def test_get_data_source_for_action(
    get_principal, principal, data_source, action, response, error_code
):
    with test_service_method(
        schema=DataSourceDetailResponse, response=response, error_code=error_code
    ) as context:
        context["result"] = data_source_service.get_data_source_for_action(
            principal=get_principal(principal), uid=data_source, action=action
        )


@pytest.mark.parametrize(
    "principal, orchestration_system, workspace, response, error_code",
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
    get_principal, principal, orchestration_system, workspace, response, error_code
):
    with test_service_method(
        schema=OrchestrationSystemDetailResponse, response=response, error_code=error_code
    ) as context:
        workspace = Workspace.objects.get(pk=workspace)
        context["result"] = data_source_service.validate_orchestration_system(
            principal=get_principal(principal),
            orchestration_system_id=orchestration_system,
            workspace=workspace,
        )


@pytest.mark.parametrize(
    "crontab, interval, interval_units, data_source, response, error_code",
    [
        (
            "* * * * *",
            None,
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
            None,
        ),
        (
            "* * * * *",
            5,
            "minutes",
            None,
            "Only one of",
            400,
        ),
        (
            "* * * * *",
            5,
            None,
            None,
            "Only one of",
            400,
        ),
        (
            "* * * * *",
            None,
            "minutes",
            None,
            "Only one of",
            400,
        ),
        (
            "invalid",
            None,
            None,
            None,
            "Invalid crontab schedule",
            400,
        ),
        (
            None,
            5,
            None,
            None,
            "Both interval and interval units",
            400,
        ),
        (
            None,
            None,
            "minutes",
            None,
            "Both interval and interval units",
            400,
        ),
    ],
)
def test_validate_scheduling(
    crontab, interval, interval_units, data_source, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.validate_scheduling(
            interval=interval,
            interval_units=interval_units,
            crontab=crontab,
        )


@pytest.mark.parametrize(
    "principal, data, response, error_code",
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
            "apikey",
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
def test_create_data_source(get_principal, principal, data, response, error_code):
    data_source_body = DataSourcePostBody(
        name=data["name"],
        workspace_id=data["workspace_id"],
        orchestration_system_id=data["orchestration_system_id"],
    )
    with test_service_method(
        schema=DataSourceDetailResponse,
        response=response or data,
        error_code=error_code,
        fields=(
            "name",
        ),
    ) as context:
        context["result"] = data_source_service.create(
            principal=get_principal(principal), data=data_source_body
        )


@pytest.mark.parametrize(
    "principal, data_source, data, response, error_code",
    [
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "Data source does not exist",
            404,
        ),
        (
            None,
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "orchestration_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "Data source does not exist",
            404,
        ),
    ],
)
def test_update_data_source(
    get_principal, principal, data_source, data, response, error_code
):
    data_source_body = DataSourcePatchBody(
        name=data["name"], orchestration_system_id=data["orchestration_system_id"]
    )
    with test_service_method(
        schema=DataSourceDetailResponse,
        response=response or data,
        error_code=error_code,
        fields=("name",),
    ) as context:
        context["result"] = data_source_service.update(
            principal=get_principal(principal), uid=data_source, data=data_source_body
        )


@pytest.mark.parametrize(
    "principal, data_source, response, error_code",
    [
        ("admin", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), None, None),
        ("owner", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), None, None),
        ("editor", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), None, None),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "Data source does not exist",
            404,
        ),
        (
            None,
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "Data source does not exist",
            404,
        ),
    ],
)
def test_delete_data_source(
    get_principal, principal, data_source, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.delete(
            principal=get_principal(principal),
            uid=data_source,
        )


@pytest.mark.parametrize(
    "principal, data_source, datastream, response, error_code",
    [
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("e0506cac-3e50-4d0a-814d-7ae0146705b2"),
            None,
            None,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "Datastream has already been linked",
            400,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("9f96957b-ee20-4c7b-bf2b-673a0cda3a04"),
            "The datastream must share a workspace",
            400,
        ),
    ],
)
def test_link_datastream(
    get_principal, principal, data_source, datastream, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.link_datastream(
            principal=get_principal(principal),
            uid=data_source,
            datastream_id=datastream,
        )


@pytest.mark.parametrize(
    "principal, data_source, datastream, response, error_code",
    [
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            None,
            None,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("e0506cac-3e50-4d0a-814d-7ae0146705b2"),
            "The given data source is not configured",
            400,
        ),
    ],
)
def test_unlink_datastream(
    get_principal, principal, data_source, datastream, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.unlink_datastream(
            principal=get_principal(principal),
            uid=data_source,
            datastream_id=datastream,
        )
