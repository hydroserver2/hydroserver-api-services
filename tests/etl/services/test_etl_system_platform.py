import pytest
import uuid
from ninja.errors import HttpError
from etl.services import EtlSystemPlatformService
from etl.schemas import (
    EtlSystemPlatformPostBody,
    EtlSystemPlatformPatchBody,
    EtlSystemPlatformGetResponse,
)

etl_system_platform_service = EtlSystemPlatformService()


@pytest.mark.parametrize(
    "user, workspace, length, max_queries",
    [
        ("owner", None, 3, 2),
        ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
        ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
        ("admin", None, 3, 2),
        ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
        ("admin", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
        ("editor", None, 3, 2),
        ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
        ("viewer", None, 3, 2),
        ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
        ("anonymous", None, 1, 2),
        ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 0, 2),
        ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
        ("anonymous", "00000000-0000-0000-0000-000000000000", 0, 2),
    ],
)
def test_list_etl_system_platform(
    django_assert_num_queries, get_user, user, workspace, length, max_queries
):
    with django_assert_num_queries(max_queries):
        etl_system_platform_list = etl_system_platform_service.list(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace) if workspace else None,
        )
        assert len(etl_system_platform_list) == length
        assert (
            EtlSystemPlatformGetResponse.from_orm(etl_system_platform)
            for etl_system_platform in etl_system_platform_list
        )


@pytest.mark.parametrize(
    "user, etl_system_platform, message, error_code",
    [
        (
            "owner",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Global ETL System Platform",
            None,
        ),
        (
            "owner",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "Workspace ETL System Platform",
            None,
        ),
        (
            "admin",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Global ETL System Platform",
            None,
        ),
        (
            "admin",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "Workspace ETL System Platform",
            None,
        ),
        (
            "editor",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Global ETL System Platform",
            None,
        ),
        (
            "editor",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "Workspace ETL System Platform",
            None,
        ),
        (
            "viewer",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Global ETL System Platform",
            None,
        ),
        (
            "viewer",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "Workspace ETL System Platform",
            None,
        ),
        (
            "anonymous",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Global ETL System Platform",
            None,
        ),
        (
            "anonymous",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "ETL system platform does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL system platform does not exist",
            404,
        ),
    ],
)
def test_get_etl_system_platform(
    get_user, user, etl_system_platform, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_platform_service.get(
                user=get_user(user), uid=uuid.UUID(etl_system_platform)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_platform_get = etl_system_platform_service.get(
            user=get_user(user), uid=uuid.UUID(etl_system_platform)
        )
        assert etl_system_platform_get.name == message
        assert EtlSystemPlatformGetResponse.from_orm(etl_system_platform_get)


@pytest.mark.parametrize(
    "user, workspace, message, error_code",
    [
        ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
        ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
        ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
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
    ],
)
def test_create_etl_system_platform(get_user, user, workspace, message, error_code):
    etl_system_platform_data = EtlSystemPlatformPostBody(
        name="New",
        interval_schedule_supported=True,
        crontab_schedule_supported=True,
        workspace_id=uuid.UUID(workspace),
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_platform_service.create(
                user=get_user(user), data=etl_system_platform_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_platform_create = etl_system_platform_service.create(
            user=get_user(user), data=etl_system_platform_data
        )
        assert etl_system_platform_create.name == etl_system_platform_data.name
        assert (
            etl_system_platform_create.interval_schedule_supported
            == etl_system_platform_data.interval_schedule_supported
        )
        assert (
            etl_system_platform_create.crontab_schedule_supported
            == etl_system_platform_data.crontab_schedule_supported
        )
        assert EtlSystemPlatformGetResponse.from_orm(etl_system_platform_create)


@pytest.mark.parametrize(
    "user, etl_system_platform, message, error_code",
    [
        (
            "owner",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        ("owner", "b3d13d31-95a1-482e-a35b-ae24e78d519e", None, None),
        ("admin", "ff0f462f-7456-40d7-93b6-77806176d08f", None, None),
        ("admin", "b3d13d31-95a1-482e-a35b-ae24e78d519e", None, None),
        (
            "editor",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        ("editor", "b3d13d31-95a1-482e-a35b-ae24e78d519e", None, None),
        (
            "viewer",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "ETL system platform does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL system platform does not exist",
            404,
        ),
    ],
)
def test_edit_etl_system_platform(
    get_user, user, etl_system_platform, message, error_code
):
    etl_system_platform_data = EtlSystemPlatformPatchBody(
        name="New", interval_schedule_supported=True, crontab_schedule_supported=True
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_platform_service.update(
                user=get_user(user),
                uid=uuid.UUID(etl_system_platform),
                data=etl_system_platform_data,
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_platform_update = etl_system_platform_service.update(
            user=get_user(user),
            uid=uuid.UUID(etl_system_platform),
            data=etl_system_platform_data,
        )
        assert etl_system_platform_update.name == etl_system_platform_data.name
        assert (
            etl_system_platform_update.interval_schedule_supported
            == etl_system_platform_data.interval_schedule_supported
        )
        assert (
            etl_system_platform_update.crontab_schedule_supported
            == etl_system_platform_data.crontab_schedule_supported
        )
        assert EtlSystemPlatformGetResponse.from_orm(etl_system_platform_update)


@pytest.mark.parametrize(
    "user, etl_system_platform, message, error_code",
    [
        (
            "owner",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        ("owner", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", None, None),
        (
            "admin",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "ETL system platform has one or more active instances",
            409,
        ),
        ("admin", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", None, None),
        (
            "editor",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        ("editor", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", None, None),
        (
            "viewer",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "ETL system platform does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL system platform does not exist",
            404,
        ),
    ],
)
def test_delete_etl_system_platform(
    get_user, user, etl_system_platform, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_platform_service.delete(
                user=get_user(user), uid=uuid.UUID(etl_system_platform)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_platform_delete = etl_system_platform_service.delete(
            user=get_user(user), uid=uuid.UUID(etl_system_platform)
        )
        assert etl_system_platform_delete == "ETL system platform deleted"
