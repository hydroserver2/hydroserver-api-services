import pytest
import json
import re
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/account'


@pytest.mark.parametrize('endpoint, method, user, expected_response_code, request_body, expected_response', [
    (  # Test GET anonymous user.
            'user', 'get', 'anonymous', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test GET active user.
            'user', 'get', 'alice', 200, None,
            '{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "middleName": null, "phone": null, "address": null, "type": "Other", "link": null, "organization": {"code": "USU", "name": "Utah State University", "description": null, "type": "Educational Institution", "link": "https://usu.edu"}, "isVerified": true, "hydroShareConnected": false}'
    ),
    (  # Test GET unverified user.
            'user', 'get', 'dave', 200, None,
            '{"firstName": "Dave", "lastName": "Brown", "email": "dave@example.com", "middleName": null, "phone": null, "address": null, "type": "Other", "link": null, "organization": null, "isVerified": false, "hydroShareConnected": false}'
    ),
    (  # Test GET inactive user.
            'user', 'get', 'emily', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test valid account creation.
            'user', 'post', 'anonymous', 200, {
                'firstName': 'John',
                'lastName': 'Hancock',
                'email': 'hancock@example.com',
                'password': 'pass'
            }, None
    ),
    (  # Test account creation with null password.
            'user', 'post', 'anonymous', 422, {
                'firstName': 'John',
                'lastName': 'Hancock',
                'email': 'hancock@example.com',
                'password': None
            },
            '{"detail": [{"type": "string_type", "loc": ["body", "data", "password"], "msg": "Input should be a valid string"}]}'
    ),
    (  # Test account creation with null required field.
            'user', 'post', 'anonymous', 422, {
                'firstName': None,
                'lastName': 'Hancock',
                'email': 'hancock@example.com',
                'password': 'pass'
            },
            '{"detail": [{"type": "string_type", "loc": ["body", "data", "firstName"], "msg": "Input should be a valid string"}]}'
    ),
    (  # Test account creation with missing required field.
            'user', 'post', 'anonymous', 422, {
                'lastName': 'Hancock',
                'email': 'hancock@example.com',
                'password': 'pass'
            },
            '{"detail": [{"type": "missing", "loc": ["body", "data", "firstName"], "msg": "Field required"}]}'
    ),
    (  # Test account creation with invalid email address.
            'user', 'post', 'anonymous', 422, {
                'firstName': 'John',
                'lastName': 'Hancock',
                'email': 'john',
                'password': 'pass'
            },
            '{"detail": [{"type": "value_error", "loc": ["body", "data", "email"], "msg": "value is not a valid email address: An email address must have an @-sign.", "ctx": {"reason": "An email address must have an @-sign."}}]}'
    ),
    (  # Test account creation with existing email address.
            'user', 'post', 'anonymous', 409, {
                'firstName': 'John',
                'lastName': 'Hancock',
                'email': 'alice@example.com',
                'password': 'pass'
            },
            '"Email already linked to an existing account."'
    ),
    (  # Test anonymous user verification email.
            'send-verification-email', 'post', 'anonymous', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test verified user verification email.
            'send-verification-email', 'post', 'alice', 403, None,
            '"Email address has already been verified for this account."'
    ),
    (  # Test unverified user verification email.
            'send-verification-email', 'post', 'dave', 200, None,
            '"Verification email sent."'
    ),
    (  # Test inactive user verification email.
            'send-verification-email', 'post', 'emily', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test anonymous user verification email.
            'send-verification-email', 'post', 'anonymous', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test verified user verification email.
            'send-verification-email', 'post', 'alice', 403, None,
            '"Email address has already been verified for this account."'
    ),
    (  # Test unverified user verification email.
            'send-verification-email', 'post', 'dave', 200, None,
            '"Verification email sent."'
    ),
    (  # Test inactive user verification email.
            'send-verification-email', 'post', 'emily', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test password reset for active user.
            'send-password-reset-email', 'post', 'anonymous', 200,
            {'email': 'alice@example.com'},
            '"Password reset email sent."'
    ),
    (  # Test password reset for anonymous user.
            'send-password-reset-email', 'post', 'anonymous', 404,
            {'email': 'anonymous@example.com'},
            '"User with the given email not found."'
    ),
    (  # Test password reset for unverified user.
            'send-password-reset-email', 'post', 'anonymous', 404,
            {'email': 'dave@example.com'},
            '"User with the given email not found."'
    ),
    (  # Test password reset for inactive user.
            'send-password-reset-email', 'post', 'anonymous', 404,
            {'email': 'emily@example.com'},
            '"User with the given email not found."'
    ),
    (  # Test PATCH with valid field changes.
            'user', 'patch', 'alice', 200,
            {'firstName': 'Alice'},
            '{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "middleName": null, "phone": null, "address": null, "type": "Other", "link": null, "organization": {"code": "USU", "name": "Utah State University", "description": null, "type": "Educational Institution", "link": "https://usu.edu"}, "isVerified": true, "hydroShareConnected": false}'
    ),
    (  # Test PATCH with no field changes.
            'user', 'patch', 'alice', 422,
            {},
            '{"detail": [{"type": "missing", "loc": ["body", "data"], "msg": "Field required"}]}'
    ),
    (  # Test PATCH changing non-nullable field to null.
            'user', 'patch', 'alice', 422,
            {'firstName': None},
            '{"detail": [{"type": "string_type", "loc": ["body", "data", "firstName"], "msg": "Input should be a valid string"}]}'
    ),
    (  # Test PATCH with anonymous user.
            'user', 'patch', 'anonymous', 401,
            {},
            '{"detail": "Unauthorized"}'
    ),
    (  # Test PATCH with unverified user.
            'user', 'patch', 'dave', 200,
            {'firstName': 'Dave'},
            '{"firstName": "Dave", "lastName": "Brown", "email": "dave@example.com", "middleName": null, "phone": null, "address": null, "type": "Other", "link": null, "organization": null, "isVerified": false, "hydroShareConnected": false}'
    ),
    (  # Test PATCH with inactive user.
            'user', 'patch', 'emily', 401,
            {},
            '{"detail": "Unauthorized"}'
    ),
    (  # Test GET API Keys for active user.
            'api-keys', 'get', 'alice', 200, None,
            '[{"name": "Alice - Data Loader Key", "permissions": [{"model": "Datastream", "methods": ["GET"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": null}, {"model": "Observation", "methods": ["GET", "POST"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": null}, {"model": "DataSource", "methods": ["GET", "PATCH"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": ["dataSourceThru", "lastSyncSuccessful", "lastSyncMessage", "lastSynced", "nextSync"]}], "expires": null, "enabled": true, "lastUsed": null, "id": "ba802221-0d79-4918-87c9-ba39193c7e9d"}, {"name": "Alice - Expired Key", "permissions": [{"model": "Thing", "methods": ["GET"], "resources": [{"model": "Thing", "ids": ["80037b7c-f833-472a-a0d1-7bc40e015ea7"]}], "fields": null}], "expires": "2000-01-01T17:00:00Z", "enabled": true, "lastUsed": null, "id": "67915a8a-4a2a-4932-8130-f2ee8ebcd6b0"}, {"name": "Alice - Disabled Key", "permissions": [{"model": "Thing", "methods": ["GET"], "resources": [{"model": "Thing", "ids": ["80037b7c-f833-472a-a0d1-7bc40e015ea7"]}], "fields": null}], "expires": null, "enabled": false, "lastUsed": null, "id": "06bb1f74-ce37-419f-8550-4843e78f8c87"}]'
    ),
    (  # Test GET one API Key for active user.
            'api-keys/ba802221-0d79-4918-87c9-ba39193c7e9d', 'get', 'alice', 200, None,
            '{"name": "Alice - Data Loader Key", "permissions": [{"model": "Datastream", "methods": ["GET"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": null}, {"model": "Observation", "methods": ["GET", "POST"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": null}, {"model": "DataSource", "methods": ["GET", "PATCH"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": ["dataSourceThru", "lastSyncSuccessful", "lastSyncMessage", "lastSynced", "nextSync"]}], "expires": null, "enabled": true, "lastUsed": null, "id": "ba802221-0d79-4918-87c9-ba39193c7e9d"}'
    ),
    (  # Test GET API Keys as anonymous user.
            'api-keys', 'get', 'anonymous', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test GET unowned API Key.
            'api-keys/ba802221-0d79-4918-87c9-ba39193c7e9d', 'get', 'bob', 404, None,
            '"API key not found."'
    ),
    (  # Test GET unowned API Key as anonymous user.
            'api-keys/ba802221-0d79-4918-87c9-ba39193c7e9d', 'get', 'anonymous', 401, None,
            '{"detail": "Unauthorized"}'
    ),
    (  # Test POST API Key as an active user.
            'api-keys', 'post', 'alice', 201,
            {
                'name': 'Test API Key',
                'permissions': [
                    {
                        'model': 'Thing', 'methods': ['GET'],
                        'resources': [{'model': 'Thing', 'ids': ['3fa85f64-5717-4562-b3fc-2c963f66afa6']}]
                    }
                ],
                'enabled': True
            }, None
    ),
    (  # Test POST API Key as an anonymous user.
            'api-keys', 'post', 'anonymous', 401,
            {
                'name': 'Test API Key',
                'permissions': [
                    {
                        'model': 'Thing', 'methods': ['GET'],
                        'resources': [{'model': 'Thing', 'ids': ['3fa85f64-5717-4562-b3fc-2c963f66afa6']}]
                    }
                ],
                'enabled': True
            }, None
    ),
    (  # Test PATCH API Key as an active user.
            'api-keys/ba802221-0d79-4918-87c9-ba39193c7e9d', 'patch', 'alice', 203,
            {
                'name': 'Test API Key',
            },
            '{"name": "Test API Key", "permissions": [{"model": "Datastream", "methods": ["GET"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": null}, {"model": "Observation", "methods": ["GET", "POST"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": null}, {"model": "DataSource", "methods": ["GET", "PATCH"], "resources": [{"model": "DataLoader", "ids": ["9d571b4b-c986-4fa8-8933-0491ddad9e0e"]}], "fields": ["dataSourceThru", "lastSyncSuccessful", "lastSyncMessage", "lastSynced", "nextSync"]}], "expires": null, "enabled": true, "lastUsed": null, "id": "ba802221-0d79-4918-87c9-ba39193c7e9d"}'
    ),
    (  # Test PATCH API Key non-nullable field with null as an active user.
            'api-keys/ba802221-0d79-4918-87c9-ba39193c7e9d', 'patch', 'alice', 422,
            {
                'name': None,
            },
            '{"detail": [{"type": "string_type", "loc": ["body", "data", "name"], "msg": "Input should be a valid string"}]}'
    ),
    (  # Test PATCH API Key as an unauthorized user.
            'api-keys/ba802221-0d79-4918-87c9-ba39193c7e9d', 'patch', 'bob', 404,
            {
                'name': 'Test API Key',
            },
            '"API key not found."'
    ),
])
@pytest.mark.django_db()
def test_account_api_endpoints(
        auth_headers, base_url, endpoint, method, user, expected_response_code, request_body, expected_response
):
    client = Client()

    request_kwargs = {
        'path': f'{base_url}/{endpoint}',
        **auth_headers[user]
    }

    if request_body:
        request_kwargs = {**request_kwargs, 'data': json.dumps(request_body), 'content_type': 'application/json'}

    response = getattr(client, method)(**request_kwargs)

    print(response.content)

    assert response.status_code == expected_response_code

    if expected_response is not None:
        if isinstance(expected_response, str):
            assert response.content.decode('utf-8') == expected_response
        else:
            expected_response = re.compile(next(iter(expected_response)))
            assert expected_response.fullmatch(response.content.decode('utf-8')), \
                'Test response did not match the expected response'
