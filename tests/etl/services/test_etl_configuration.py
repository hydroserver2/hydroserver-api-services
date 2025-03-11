import pytest
import uuid
from ninja.errors import HttpError
from etl.services import EtlConfigurationService
from etl.schemas import EtlConfigurationPostBody, EtlConfigurationPatchBody, EtlConfigurationGetResponse

etl_configuration_service = EtlConfigurationService()


@pytest.mark.parametrize("user, workspace, etl_system_platform, length, max_queries", [
    ("admin", None, None, 5, 2),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 3, 2),
    ("admin", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 2, 2),
    ("owner", None, None, 5, 2),
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 3, 2),
    ("owner", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 2, 2),
    ("editor", None, None, 5, 2),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 3, 2),
    ("editor", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 2, 2),
    ("viewer", None, None, 5, 2),
    ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 3, 2),
    ("viewer", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 2, 2),
    ("anonymous", None, None, 2, 2),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 0, 2),
    ("anonymous", None, "b3d13d31-95a1-482e-a35b-ae24e78d519e", 0, 2),
    ("anonymous", "00000000-0000-0000-0000-000000000000", None, 0, 2),
    ("anonymous", None, "00000000-0000-0000-0000-000000000000", 0, 2),
])
def test_list_etl_configuration(django_assert_num_queries, get_user, user, workspace, etl_system_platform, length,
                                max_queries):
    with django_assert_num_queries(max_queries):
        etl_configuration_list = etl_configuration_service.list(
            user=get_user(user), workspace_id=uuid.UUID(workspace) if workspace else None,
            etl_system_platform_id=uuid.UUID(etl_system_platform) if etl_system_platform else None
        )
        assert len(etl_configuration_list) == length
        assert (EtlConfigurationGetResponse.from_orm(etl_configuration) for etl_configuration in etl_configuration_list)


@pytest.mark.parametrize("user, etl_system_platform, etl_configuration, message, error_code", [
    ("admin", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "Global Data Source Configuration", None),
    ("admin", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", "Workspace Data Source Configuration", None),
    ("owner", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "Global Data Source Configuration", None),
    ("owner", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", "Workspace Data Source Configuration", None),
    ("editor", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "Global Data Source Configuration", None),
    ("editor", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", "Workspace Data Source Configuration", None),
    ("viewer", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "Global Data Source Configuration", None),
    ("viewer", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", "Workspace Data Source Configuration", None),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "Global Data Source Configuration", None),
    ("anonymous", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", "ETL configuration does not exist", 404),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", "00000000-0000-0000-0000-000000000000", "ETL configuration does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "ETL system platform does not exist", 404),
])
def test_get_etl_configuration(get_user, user, etl_system_platform, etl_configuration, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_configuration_service.get(
                user=get_user(user), uid=uuid.UUID(etl_configuration),
                etl_system_platform_id=uuid.UUID(etl_system_platform)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_configuration_get = etl_configuration_service.get(
            user=get_user(user), uid=uuid.UUID(etl_configuration), etl_system_platform_id=uuid.UUID(etl_system_platform)
        )
        assert etl_configuration_get.name == message
        assert EtlConfigurationGetResponse.from_orm(etl_configuration_get)


@pytest.mark.parametrize("user, etl_system_platform, etl_configuration_schema, message, error_code", [
    ("admin", "ff0f462f-7456-40d7-93b6-77806176d08f", {}, "You do not have permission", 403),
    ("admin", "b3d13d31-95a1-482e-a35b-ae24e78d519e", {}, None, None),
    ("admin", "b3d13d31-95a1-482e-a35b-ae24e78d519e", {"type": "unknown"}, "'unknown' is not valid", 400),
    ("owner", "ff0f462f-7456-40d7-93b6-77806176d08f", {}, "You do not have permission", 403),
    ("owner", "b3d13d31-95a1-482e-a35b-ae24e78d519e", {}, None, None),
    ("editor", "ff0f462f-7456-40d7-93b6-77806176d08f", {}, "You do not have permission", 403),
    ("editor", "b3d13d31-95a1-482e-a35b-ae24e78d519e", {}, None, None),
    ("viewer", "ff0f462f-7456-40d7-93b6-77806176d08f", {}, "You do not have permission", 403),
    ("viewer", "b3d13d31-95a1-482e-a35b-ae24e78d519e", {}, "You do not have permission", 403),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", {}, "You do not have permission", 403),
    ("anonymous", "b3d13d31-95a1-482e-a35b-ae24e78d519e", {}, "ETL system platform does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", {}, "ETL system platform does not exist", 404),
])
def test_create_etl_configuration(get_user, user, etl_system_platform, etl_configuration_schema, message, error_code):
    etl_configuration_data = EtlConfigurationPostBody(
        name="New", etl_configuration_type="DataSource", etl_configuration_schema=etl_configuration_schema
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_configuration_service.create(
                user=get_user(user), etl_system_platform_id=uuid.UUID(etl_system_platform), data=etl_configuration_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_configuration_create = etl_configuration_service.create(
            user=get_user(user), etl_system_platform_id=uuid.UUID(etl_system_platform), data=etl_configuration_data
        )
        assert etl_configuration_create.name == etl_configuration_data.name
        assert EtlConfigurationGetResponse.from_orm(etl_configuration_create)


@pytest.mark.parametrize("user, etl_system_platform, etl_configuration, etl_configuration_schema, message, error_code", [
    ("admin", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", {}, None, None),
    ("admin", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", {}, None, None),
    ("admin", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", {"type": "unknown"}, "'unknown' is not valid", 400),
    ("owner", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", {}, "You do not have permission", 403),
    ("owner", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", {}, None, None),
    ("editor", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", {}, "You do not have permission", 403),
    ("editor", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", {}, None, None),
    ("viewer", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", {}, "You do not have permission", 403),
    ("viewer", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", {}, "You do not have permission", 403),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", {}, "You do not have permission", 403),
    ("anonymous", "b3d13d31-95a1-482e-a35b-ae24e78d519e", "0f73cc35-0cd5-45d3-9597-65877f84a924", {}, "ETL configuration does not exist", 404),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", "00000000-0000-0000-0000-000000000000", {}, "ETL configuration does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", {}, "ETL system platform does not exist", 404),
])
def test_edit_etl_configuration(get_user, user, etl_system_platform, etl_configuration, etl_configuration_schema,
                                message, error_code):
    etl_configuration_data = EtlConfigurationPatchBody(
        name="New", etl_configuration_type="DataSource", etl_configuration_schema=etl_configuration_schema
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_configuration_service.update(
                user=get_user(user), uid=uuid.UUID(etl_configuration),
                etl_system_platform_id=uuid.UUID(etl_system_platform), data=etl_configuration_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_configuration_update = etl_configuration_service.update(
                user=get_user(user), uid=uuid.UUID(etl_configuration),
                etl_system_platform_id=uuid.UUID(etl_system_platform), data=etl_configuration_data
            )
        assert etl_configuration_update.name == etl_configuration_data.name
        assert EtlConfigurationGetResponse.from_orm(etl_configuration_update)


@pytest.mark.parametrize("user, etl_system_platform, etl_configuration, message, error_code", [
    ("admin", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "ETL configuration in use", 409),
    ("admin", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", "46f2d592-3a06-4df5-bd86-6621a8f0c347", None, None),
    ("owner", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "You do not have permission", 403),
    ("owner", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", "46f2d592-3a06-4df5-bd86-6621a8f0c347", None, None),
    ("editor", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "You do not have permission", 403),
    ("editor", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", "46f2d592-3a06-4df5-bd86-6621a8f0c347", None, None),
    ("viewer", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "You do not have permission", 403),
    ("viewer", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", "46f2d592-3a06-4df5-bd86-6621a8f0c347", "You do not have permission", 403),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", "0467a2dd-254c-49f4-9087-2e041f8ebc0c", "You do not have permission", 403),
    ("anonymous", "8fe5560d-483d-49d8-9bad-3b01d5ef3916", "46f2d592-3a06-4df5-bd86-6621a8f0c347", "ETL configuration does not exist", 404),
    ("anonymous", "ff0f462f-7456-40d7-93b6-77806176d08f", "00000000-0000-0000-0000-000000000000", "ETL configuration does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "ETL system platform does not exist", 404),
])
def test_delete_etl_configuration(get_user, user, etl_system_platform, etl_configuration, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            etl_configuration_service.delete(
                user=get_user(user), uid=uuid.UUID(etl_configuration),
                etl_system_platform_id=uuid.UUID(etl_system_platform)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        etl_configuration_delete = etl_configuration_service.delete(
            user=get_user(user), uid=uuid.UUID(etl_configuration),
            etl_system_platform_id=uuid.UUID(etl_system_platform)
        )
        assert etl_configuration_delete == "ETL configuration deleted"
