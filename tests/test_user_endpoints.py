import pytest
import json
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/account'


@pytest.mark.parametrize('endpoint, response_code, user', [
    ('user', 200, 'alice'),
])
@pytest.mark.django_db()
def test_account_list_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, response_code, user
):
    client = Client()

    response = client.get(
        f'{base_url}/{endpoint}',
        **auth_headers[user]
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, post_body, response_code', [
    ('user', {
        'firstName': 'John',
        'lastName': 'Hancock',
        'email': 'hancock@example.com',
        'password': 'pass'
    }, 200),
    ('user', {
        'firstName': 'John',
        'lastName': 'Hancock',
        'email': 'hancock@example.com',
        'password': None
    }, 422),
    ('user', {
        'firstName': None,
        'lastName': 'Hancock',
        'email': 'hancock@example.com',
        'password': 'pass'
    }, 422),
    ('user', {
        'firstName': 'John',
        'lastName': 'Hancock',
        'email': 'john',
        'password': 'pass'
    }, 422),
])
@pytest.mark.django_db()
def test_account_post_endpoints(
        base_url, endpoint, post_body, response_code
):
    client = Client()

    response = client.post(
        f'{base_url}/{endpoint}',
        json.dumps(post_body),
        content_type='application/json'
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, patch_body, response_code, user', [
    ('user', {
        'firstName': 'Alice',
    }, 200, 'alice'),
    ('user', {
        'organization': {
            'code': 'USU',
            'name': 'Utah State University',
            'type': 'University'
        }
    }, 200, 'alice'),
    ('user', {
        'firstName': None,
    }, 422, 'alice')
])
@pytest.mark.django_db()
def test_account_patch_endpoints(
        auth_headers, base_url, endpoint, patch_body, response_code, user
):
    client = Client()

    response = client.patch(
        f'{base_url}/{endpoint}',
        json.dumps(patch_body),
        content_type='application/json',
        **auth_headers[user]
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, response_code, user', [
    ('send-verification-email', 403, 'alice'),
    ('activate', 400, 'alice'),
    ('send-password-reset-email', 400, 'alice')
])
@pytest.mark.django_db()
def test_account_verification_endpoints(
        auth_headers, base_url, endpoint, response_code, user
):
    client = Client()

    response = client.post(
        f'{base_url}/{endpoint}',
        **auth_headers[user]
    )

    assert response.status_code == response_code
