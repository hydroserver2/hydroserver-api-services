import pytest
from uuid import UUID
from etl.models import EtlSystemPlatform, EtlSystem, DataSource
from iam.models import Workspace
from etl.services import DataSourceService
from etl.schemas import (
    DataSourcePostBody,
    DataSourcePatchBody,
    DataSourceGetResponse,
    EtlSystemGetResponse,
    EtlConfigurationGetResponse,
    LinkedDatastreamGetResponse,
    LinkedDatastreamPostBody,
    LinkedDatastreamPatchBody,
)
from tests.utils import test_service_method

data_source_service = DataSourceService()


@pytest.mark.parametrize(
    "user, workspace, etl_system_platform, etl_system, length, max_queries",
    [
        ("admin", None, None, None, 3, 4),
        ("admin", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, None, 0, 2),
        ("admin", None, UUID("b3d13d31-95a1-482e-a35b-ae24e78d519e"), None, 0, 2),
        ("admin", None, None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("owner", None, None, None, 3, 4),
        ("owner", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, None, 0, 2),
        ("owner", None, UUID("b3d13d31-95a1-482e-a35b-ae24e78d519e"), None, 0, 2),
        ("owner", None, None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("editor", None, None, None, 3, 4),
        ("editor", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, None, 0, 2),
        ("editor", None, UUID("b3d13d31-95a1-482e-a35b-ae24e78d519e"), None, 0, 2),
        ("editor", None, None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("viewer", None, None, None, 3, 4),
        ("viewer", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, None, 0, 2),
        ("viewer", None, UUID("b3d13d31-95a1-482e-a35b-ae24e78d519e"), None, 0, 2),
        ("viewer", None, None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
        ("anonymous", None, None, None, 0, 4),
        ("anonymous", UUID("b27c51a0-7374-462d-8a53-d97d47176c10"), None, None, 0, 2),
        ("anonymous", None, UUID("b3d13d31-95a1-482e-a35b-ae24e78d519e"), None, 0, 2),
        ("anonymous", None, None, UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"), 0, 2),
    ],
)
def test_list_data_source(
    django_assert_max_num_queries,
    get_user,
    user,
    workspace,
    etl_system_platform,
    etl_system,
    length,
    max_queries,
):
    with django_assert_max_num_queries(max_queries):
        with test_service_method(
            schema=DataSourceGetResponse, response=length
        ) as context:
            context["result"] = data_source_service.list(
                user=get_user(user),
                workspace_id=workspace if workspace else None,
                etl_system_platform_id=(
                    etl_system_platform if etl_system_platform else None
                ),
                etl_system_id=etl_system if etl_system else None,
            )


@pytest.mark.parametrize(
    "user, data_source, action, response, error_code",
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
    ],
)
def test_get_data_source_for_action(
    get_user, user, data_source, action, response, error_code
):
    with test_service_method(
        schema=DataSourceGetResponse, response=response, error_code=error_code
    ) as context:
        context["result"] = data_source_service.get_data_source_for_action(
            user=get_user(user), uid=data_source, action=action
        )


@pytest.mark.parametrize(
    "user, etl_system, workspace, response, error_code",
    [
        (
            "owner",
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
            {"name": "Global ETL System"},
            None,
        ),
        (
            "owner",
            UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"),
            UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
            {"name": "Workspace ETL System 1"},
            None,
        ),
        (
            "owner",
            UUID("ee44f263-237c-4b62-8dde-2b1b407462e2"),
            UUID("b27c51a0-7374-462d-8a53-d97d47176c10"),
            "The given ETL system cannot",
            400,
        ),
    ],
)
def test_validate_etl_system(
    get_user, user, etl_system, workspace, response, error_code
):
    with test_service_method(
        schema=EtlSystemGetResponse, response=response, error_code=error_code
    ) as context:
        workspace = Workspace.objects.get(pk=workspace)
        context["result"] = data_source_service.validate_etl_system(
            user=get_user(user), etl_system_id=etl_system, workspace=workspace
        )


@pytest.mark.parametrize(
    "user, etl_configuration, etl_system_platform, settings, response, error_code",
    [
        (
            "owner",
            UUID("0467a2dd-254c-49f4-9087-2e041f8ebc0c"),
            UUID("ff0f462f-7456-40d7-93b6-77806176d08f"),
            {"timestampColumnName": "timestamp"},
            {},
            None,
        ),
        (
            "owner",
            "0f73cc35-0cd5-45d3-9597-65877f84a924",
            UUID("ff0f462f-7456-40d7-93b6-77806176d08f"),
            {"timestampColumnName": "timestamp"},
            "The given ETL configuration cannot be used",
            400,
        ),
        (
            "owner",
            UUID("0467a2dd-254c-49f4-9087-2e041f8ebc0c"),
            UUID("ff0f462f-7456-40d7-93b6-77806176d08f"),
            {},
            "'timestampColumnName' is a required property",
            400,
        ),
    ],
)
def test_validate_etl_configuration(
    get_user,
    user,
    etl_configuration,
    etl_system_platform,
    settings,
    response,
    error_code,
):
    with test_service_method(
        schema=EtlConfigurationGetResponse, response=response, error_code=error_code
    ) as context:
        etl_system_platform = EtlSystemPlatform.objects.get(pk=etl_system_platform)
        context["result"] = data_source_service.validate_etl_configuration(
            user=get_user(user),
            etl_configuration_id=etl_configuration if etl_configuration else None,
            etl_system_platform=etl_system_platform,
            etl_configuration_settings=settings,
        )


@pytest.mark.parametrize(
    "etl_system, crontab, interval, interval_units, data_source, response, error_code",
    [
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            "* * * * *",
            None,
            None,
            None,
            None,
            None,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            None,
            5,
            "minutes",
            None,
            None,
            None,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            "* * * * *",
            5,
            "minutes",
            None,
            "Only one of",
            400,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            "* * * * *",
            5,
            None,
            None,
            "Only one of",
            400,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            "* * * * *",
            None,
            "minutes",
            None,
            "Only one of",
            400,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            "invalid",
            None,
            None,
            None,
            "Invalid crontab schedule",
            400,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            None,
            5,
            None,
            None,
            "Both interval and interval units",
            400,
        ),
        (
            UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            None,
            None,
            "minutes",
            None,
            "Both interval and interval units",
            400,
        ),
        (
            UUID("7cb900d2-eb11-4a59-a05b-dd02d95af312"),
            "* * * * *",
            None,
            None,
            None,
            "Crontab schedule not supported",
            400,
        ),
        (
            UUID("7cb900d2-eb11-4a59-a05b-dd02d95af312"),
            None,
            5,
            "minutes",
            None,
            "Interval schedule not supported",
            400,
        ),
    ],
)
def test_validate_scheduling(
    etl_system, crontab, interval, interval_units, data_source, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        etl_system = EtlSystem.objects.get(pk=etl_system)
        data_source = DataSource.objects.get(pk=data_source) if data_source else None
        context["result"] = data_source_service.validate_scheduling(
            etl_system=etl_system,
            interval=interval,
            interval_units=interval_units,
            crontab=crontab,
            data_source=data_source,
        )


@pytest.mark.parametrize(
    "user, data, response, error_code",
    [
        (
            "admin",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "owner",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "editor",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "viewer",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            {
                "name": "New",
                "workspace_id": UUID("6e0deaf2-a92b-421b-9ece-86783265596f"),
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
    ],
)
def test_create_data_source(get_user, user, data, response, error_code):
    data_source_body = DataSourcePostBody(
        name=data["name"],
        workspace_id=data["workspace_id"],
        etl_system_id=data["etl_system_id"],
    )
    with test_service_method(
        schema=DataSourceGetResponse, response=response or data, error_code=error_code
    ) as context:
        context["result"] = data_source_service.create(
            user=get_user(user), data=data_source_body
        )


@pytest.mark.parametrize(
    "user, data_source, data, response, error_code",
    [
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            None,
            None,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            {
                "name": "New",
                "etl_system_id": UUID("320ad0e1-1426-47f6-8a3a-886a7111a7c2"),
            },
            "Data source does not exist",
            404,
        ),
    ],
)
def test_update_data_source(get_user, user, data_source, data, response, error_code):
    data_source_body = DataSourcePatchBody(
        name=data["name"], etl_system_id=data["etl_system_id"]
    )
    with test_service_method(
        schema=DataSourceGetResponse, response=response or data, error_code=error_code
    ) as context:
        context["result"] = data_source_service.update(
            user=get_user(user), uid=data_source, data=data_source_body
        )


@pytest.mark.parametrize(
    "user, data_source, response, error_code",
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
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "Data source does not exist",
            404,
        ),
    ],
)
def test_delete_data_source(get_user, user, data_source, response, error_code):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.delete(
            user=get_user(user),
            uid=data_source,
        )


@pytest.mark.parametrize(
    "user, data_source, length, max_queries, error_code",
    [
        ("admin", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), 1, 6, None),
        ("owner", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), 1, 6, None),
        ("editor", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), 1, 6, None),
        ("viewer", UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"), 1, 6, None),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            "Data source does not exist",
            6,
            404,
        ),
    ],
)
def test_list_linked_datastreams(
    django_assert_max_num_queries,
    get_user,
    user,
    data_source,
    length,
    max_queries,
    error_code,
):
    with django_assert_max_num_queries(max_queries):
        with test_service_method(
            schema=LinkedDatastreamGetResponse, response=length, error_code=error_code
        ) as context:
            context["result"] = data_source_service.list_linked_datastreams(
                user=get_user(user), uid=data_source
            )


@pytest.mark.parametrize(
    "user, data_source, datastream, action, response, error_code",
    [
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "view",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "edit",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "delete",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "view",
            "Data source does not exist",
            404,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "edit",
            "Data source does not exist",
            404,
        ),
        (
            "admin",
            UUID("00000000-0000-0000-0000-000000000000"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "delete",
            "Data source does not exist",
            404,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("00000000-0000-0000-0000-000000000000"),
            "view",
            "The given datastream is not linked",
            400,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("00000000-0000-0000-0000-000000000000"),
            "edit",
            "The given datastream is not linked",
            400,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("00000000-0000-0000-0000-000000000000"),
            "delete",
            "The given datastream is not linked",
            400,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("dd5c60c2-a631-4e27-9aec-a59e1183861c"),
            "view",
            "The given datastream is not linked",
            400,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("dd5c60c2-a631-4e27-9aec-a59e1183861c"),
            "edit",
            "The given datastream is not linked",
            400,
        ),
        (
            "admin",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("dd5c60c2-a631-4e27-9aec-a59e1183861c"),
            "delete",
            "The given datastream is not linked",
            400,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "view",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "edit",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "owner",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "delete",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "view",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "edit",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "editor",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "delete",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "view",
            {"etl_configuration_id": UUID("09e6ad1f-c81c-4f32-aebc-c3f9006fafd4")},
            None,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "edit",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "delete",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "view",
            "Data source does not exist",
            404,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "edit",
            "Data source does not exist",
            404,
        ),
        (
            "anonymous",
            UUID("8bc6ba8b-dc67-4ca2-bed1-5abb4b067024"),
            UUID("27c70b41-e845-40ea-8cc7-d1b40f89816b"),
            "delete",
            "Data source does not exist",
            404,
        ),
    ],
)
def test_get_linked_datastream_for_action(
    get_user, user, data_source, datastream, action, response, error_code
):
    with test_service_method(
        schema=LinkedDatastreamGetResponse, response=response, error_code=error_code
    ) as context:
        context["result"] = data_source_service.get_linked_datastream_for_action(
            user=get_user(user),
            data_source_id=data_source,
            datastream_id=datastream,
            action=action,
        )


@pytest.mark.parametrize(
    "user, data_source, datastream, response, error_code",
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
def test_link_datastream(get_user, user, data_source, datastream, response, error_code):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.link_datastream(
            user=get_user(user),
            uid=data_source,
            datastream_id=datastream,
            data=LinkedDatastreamPostBody(),
        )


@pytest.mark.parametrize(
    "user, data_source, datastream, response, error_code",
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
            "The given datastream is not linked",
            400,
        ),
    ],
)
def test_update_linked_datastream(
    get_user, user, data_source, datastream, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.update_linked_datastream(
            user=get_user(user),
            uid=data_source,
            datastream_id=datastream,
            data=LinkedDatastreamPatchBody(),
        )


@pytest.mark.parametrize(
    "user, data_source, datastream, response, error_code",
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
            "The given datastream is not linked",
            400,
        ),
    ],
)
def test_unlink_datastream(
    get_user, user, data_source, datastream, response, error_code
):
    with test_service_method(response=response, error_code=error_code) as context:
        context["result"] = data_source_service.unlink_datastream(
            user=get_user(user), uid=data_source, datastream_id=datastream
        )
