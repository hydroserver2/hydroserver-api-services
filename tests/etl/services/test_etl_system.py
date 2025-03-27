import pytest
import uuid
from ninja.errors import HttpError
from etl.services import EtlSystemService
from etl.schemas import EtlSystemPostBody, EtlSystemPatchBody, EtlSystemGetResponse

etl_system_service = EtlSystemService()


@pytest.mark.parametrize(
    "user, workspace, etl_system_platform, length, max_queries",
    [
        ("owner", None, None, 3, 2),
        ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 2, 2),
        ("owner", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 1, 2),
        ("admin", None, None, 3, 2),
        ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 2, 2),
        ("admin", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 1, 2),
        ("editor", None, None, 3, 2),
        ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 2, 2),
        ("editor", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 1, 2),
        ("viewer", None, None, 3, 2),
        ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 2, 2),
        ("viewer", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 1, 2),
        ("anonymous", None, None, 1, 2),
        ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 0, 2),
        ("anonymous", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 0, 2),
        ("anonymous", "00000000-0000-0000-0000-000000000000", None, 0, 2),
        ("anonymous", None, "00000000-0000-0000-0000-000000000000", 0, 2),
    ],
)
def test_list_etl_system(
    django_assert_num_queries,
    get_user,
    user,
    workspace,
    etl_system_platform,
    length,
    max_queries,
):
    with django_assert_num_queries(max_queries):
        etl_system_list = etl_system_service.list(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace) if workspace else None,
            etl_system_platform_id=(
                uuid.UUID(etl_system_platform) if etl_system_platform else None
            ),
        )
        assert len(etl_system_list) == length
        assert (
            EtlSystemGetResponse.from_orm(etl_system) for etl_system in etl_system_list
        )


@pytest.mark.parametrize(
    "user, etl_system, message, error_code",
    [
        ("owner", "320ad0e1-1426-47f6-8a3a-886a7111a7c2", "Global ETL System", None),
        (
            "owner",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "Workspace ETL System 1",
            None,
        ),
        (
            "owner",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "Workspace ETL System 2",
            None,
        ),
        ("admin", "320ad0e1-1426-47f6-8a3a-886a7111a7c2", "Global ETL System", None),
        (
            "admin",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "Workspace ETL System 1",
            None,
        ),
        (
            "admin",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "Workspace ETL System 2",
            None,
        ),
        ("editor", "320ad0e1-1426-47f6-8a3a-886a7111a7c2", "Global ETL System", None),
        (
            "editor",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "Workspace ETL System 1",
            None,
        ),
        (
            "editor",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "Workspace ETL System 2",
            None,
        ),
        ("viewer", "320ad0e1-1426-47f6-8a3a-886a7111a7c2", "Global ETL System", None),
        (
            "viewer",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "Workspace ETL System 1",
            None,
        ),
        (
            "viewer",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "Workspace ETL System 2",
            None,
        ),
        (
            "anonymous",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "Global ETL System",
            None,
        ),
        (
            "anonymous",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "ETL system does not exist",
            404,
        ),
        (
            "anonymous",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "ETL system does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL system does not exist",
            404,
        ),
    ],
)
def test_get_etl_system(get_user, user, etl_system, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_service.get(user=get_user(user), uid=uuid.UUID(etl_system))
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_get = etl_system_service.get(
            user=get_user(user), uid=uuid.UUID(etl_system)
        )
        assert etl_system_get.name == message
        assert EtlSystemGetResponse.from_orm(etl_system_get)


@pytest.mark.parametrize(
    "user, workspace, etl_system_platform, message, error_code",
    [
        (
            "admin",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            None,
            None,
        ),
        (
            "admin",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            None,
            None,
        ),
        (
            "admin",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            None,
            None,
        ),
        (
            "admin",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "ETL systems must share a workspace",
            400,
        ),
        (
            "admin",
            "00000000-0000-0000-0000-000000000000",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Workspace does not exist",
            404,
        ),
        (
            "admin",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "00000000-0000-0000-0000-000000000000",
            "ETL system platform does not exist",
            400,
        ),
        (
            "owner",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            None,
            None,
        ),
        (
            "owner",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            None,
            None,
        ),
        (
            "owner",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            None,
            None,
        ),
        (
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            None,
            None,
        ),
        (
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            None,
            None,
        ),
        (
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            None,
            None,
        ),
        (
            "viewer",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "b3d13d31-95a1-482e-a35b-ae24e78d519e",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ff0f462f-7456-40d7-93b6-77806176d08f",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "00000000-0000-0000-0000-000000000000",
            "You do not have permission",
            403,
        ),
    ],
)
def test_create_etl_system(
    get_user, user, workspace, etl_system_platform, message, error_code
):
    etl_system_data = EtlSystemPostBody(
        name="New",
        etl_system_platform_id=uuid.UUID(etl_system_platform),
        workspace_id=uuid.UUID(workspace),
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_service.create(user=get_user(user), data=etl_system_data)
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_create = etl_system_service.create(
            user=get_user(user), data=etl_system_data
        )
        assert etl_system_create.name == etl_system_data.name
        assert EtlSystemGetResponse.from_orm(etl_system_create)


@pytest.mark.parametrize(
    "user, etl_system, message, error_code",
    [
        ("admin", "320ad0e1-1426-47f6-8a3a-886a7111a7c2", None, None),
        ("admin", "ee44f263-237c-4b62-8dde-2b1b407462e2", None, None),
        ("admin", "7cb900d2-eb11-4a59-a05b-dd02d95af312", None, None),
        (
            "owner",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        ("owner", "ee44f263-237c-4b62-8dde-2b1b407462e2", None, None),
        ("owner", "7cb900d2-eb11-4a59-a05b-dd02d95af312", None, None),
        (
            "editor",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        ("editor", "ee44f263-237c-4b62-8dde-2b1b407462e2", None, None),
        ("editor", "7cb900d2-eb11-4a59-a05b-dd02d95af312", None, None),
        (
            "viewer",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "ETL system does not exist",
            404,
        ),
        (
            "anonymous",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "ETL system does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL system does not exist",
            404,
        ),
    ],
)
def test_edit_etl_system(get_user, user, etl_system, message, error_code):
    etl_system_data = EtlSystemPatchBody(name="New")
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_service.update(
                user=get_user(user), uid=uuid.UUID(etl_system), data=etl_system_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_update = etl_system_service.update(
            user=get_user(user), uid=uuid.UUID(etl_system), data=etl_system_data
        )
        assert etl_system_update.name == etl_system_data.name
        assert EtlSystemGetResponse.from_orm(etl_system_update)


@pytest.mark.parametrize(
    "user, etl_system, message, error_code",
    [
        ("admin", "320ad0e1-1426-47f6-8a3a-886a7111a7c2", "ETL system in use", 409),
        ("admin", "ee44f263-237c-4b62-8dde-2b1b407462e2", None, None),
        ("admin", "7cb900d2-eb11-4a59-a05b-dd02d95af312", None, None),
        (
            "owner",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        ("owner", "ee44f263-237c-4b62-8dde-2b1b407462e2", None, None),
        ("owner", "7cb900d2-eb11-4a59-a05b-dd02d95af312", None, None),
        (
            "editor",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        ("editor", "ee44f263-237c-4b62-8dde-2b1b407462e2", None, None),
        ("editor", "7cb900d2-eb11-4a59-a05b-dd02d95af312", None, None),
        (
            "viewer",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "320ad0e1-1426-47f6-8a3a-886a7111a7c2",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "ee44f263-237c-4b62-8dde-2b1b407462e2",
            "ETL system does not exist",
            404,
        ),
        (
            "anonymous",
            "7cb900d2-eb11-4a59-a05b-dd02d95af312",
            "ETL system does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "ETL system does not exist",
            404,
        ),
    ],
)
def test_delete_etl_system(get_user, user, etl_system, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_system_service.delete(user=get_user(user), uid=uuid.UUID(etl_system))
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_system_delete = etl_system_service.delete(
            user=get_user(user), uid=uuid.UUID(etl_system)
        )
        assert etl_system_delete == "ETL system deleted"
