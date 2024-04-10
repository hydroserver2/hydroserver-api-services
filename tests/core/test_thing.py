import pytest
import json
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/data'


@pytest.mark.parametrize('endpoint, query_params, response_code, response_length, max_queries, user', [
    ('things', {}, 200, 2, 3, 'anonymous'),
    ('things', {}, 200, 4, 4, 'alice'),
    ('things', {'modified_since': '2090-01-01T11:11:11Z'}, 200, 0, 3, 'anonymous'),
    ('things', {'owned_only': True}, 200, 2, 4, 'bob'),
    ('things', {'owned_only': True}, 200, 0, 4, 'anonymous'),
    ('things', {'primary_owned_only': True}, 200, 4, 4, 'alice'),
    ('things', {'primary_owned_only': True}, 200, 0, 4, 'anonymous'),
    ('observed-properties', {}, 200, 3, 3, 'anonymous'),
    ('observed-properties', {}, 200, 3, 3, 'alice'),
    ('observed-properties', {'owner': 'currentUser'}, 200, 1, 3, 'alice'),
    ('observed-properties', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('observed-properties', {'owner': 'currentUserOrNoUser'}, 200, 2, 3, 'alice'),
    ('observed-properties', {'owner': 'anyUser'}, 200, 2, 3, 'alice'),
    ('observed-properties', {'owner': 'anyUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('processing-levels', {}, 200, 3, 3, 'anonymous'),
    ('processing-levels', {}, 200, 3, 3, 'alice'),
    ('processing-levels', {'owner': 'currentUser'}, 200, 1, 3, 'alice'),
    ('processing-levels', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('processing-levels', {'owner': 'currentUserOrNoUser'}, 200, 2, 3, 'alice'),
    ('processing-levels', {'owner': 'anyUser'}, 200, 2, 3, 'alice'),
    ('processing-levels', {'owner': 'anyUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('result-qualifiers', {}, 200, 4, 3, 'anonymous'),
    ('result-qualifiers', {}, 200, 4, 3, 'alice'),
    ('result-qualifiers', {'owner': 'currentUser'}, 200, 2, 3, 'alice'),
    ('result-qualifiers', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('result-qualifiers', {'owner': 'currentUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('result-qualifiers', {'owner': 'anyUser'}, 200, 3, 3, 'alice'),
    ('result-qualifiers', {'owner': 'anyUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('sensors', {}, 200, 3, 3, 'anonymous'),
    ('sensors', {}, 200, 3, 3, 'alice'),
    ('sensors', {'owner': 'currentUser'}, 200, 1, 3, 'alice'),
    ('sensors', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('sensors', {'owner': 'currentUserOrNoUser'}, 200, 2, 3, 'alice'),
    ('sensors', {'owner': 'anyUser'}, 200, 2, 3, 'alice'),
    ('sensors', {'owner': 'anyUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('units', {}, 200, 4, 3, 'anonymous'),
    ('units', {}, 200, 4, 3, 'alice'),
    ('units', {'owner': 'currentUser'}, 200, 2, 3, 'alice'),
    ('units', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('units', {'owner': 'currentUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('units', {'owner': 'anyUser'}, 200, 3, 3, 'alice'),
    ('units', {'owner': 'anyUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('data-loaders', {}, 200, 0, 3, 'anonymous'),
    ('data-loaders', {}, 200, 1, 3, 'alice'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', {}, 404, 1, 3, 'anonymous'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', {}, 404, 1, 3, 'bob'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', {}, 200, 1, 3, 'alice'),
    ('data-sources', {}, 200, 0, 3, 'anonymous'),
    ('data-sources', {}, 200, 1, 3, 'alice'),
])
@pytest.mark.django_db()
def test_core_list_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, query_params, response_code, response_length,
        max_queries, user
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.get(
            f'{base_url}/{endpoint}',
            query_params,
            **auth_headers[user]
        )

    assert response.status_code == response_code

    if response_length is not None:
        data = json.loads(response.content)
        assert len(data) == response_length


@pytest.mark.parametrize('endpoint, response_code, max_queries, user', [
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1', 200, 4, 'anonymous'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7', 404, 4, 'anonymous'),
    ('things/00000000-0000-0000-0000-000000000000', 404, 4, 'anonymous'),
    ('things/92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7', 404, 4, 'anonymous'),
    ('things/819260c8-2543-4046-b8c4-7431243ed7c5', 200, 4, 'alice'),
    ('things/819260c8-2543-4046-b8c4-7431243ed7c5', 200, 4, 'bob'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7', 404, 4, 'bob'),
    ('observed-properties/11e37e36-3d65-497a-b432-e238ec45195b', 200, 2, 'anonymous'),
    ('observed-properties/11e37e36-3d65-497a-b432-e238ec45195b', 200, 2, 'alice'),
    ('observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 200, 2, 'anonymous'),
    ('observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 200, 2, 'alice'),
    ('observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 200, 2, 'bob'),
    ('observed-properties/00000000-0000-0000-0000-000000000000', 404, 2, 'anonymous'),
    ('observed-properties/b6bfee6e-b8d6-46cd-972a-bdd56bd41bd1', 404, 2, 'anonymous'),
    ('processing-levels/caab642c-14f9-4823-8517-9b1bce59f626', 200, 2, 'anonymous'),
    ('processing-levels/caab642c-14f9-4823-8517-9b1bce59f626', 200, 2, 'alice'),
    ('processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 200, 2, 'anonymous'),
    ('processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 200, 2, 'alice'),
    ('processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 200, 2, 'bob'),
    ('processing-levels/00000000-0000-0000-0000-000000000000', 404, 2, 'anonymous'),
    ('processing-levels/2a92ca50-fe96-438b-bc1c-7efb09427383', 404, 2, 'anonymous'),
    ('result-qualifiers/7a6a3957-f45f-4a00-9edf-d1e53a689538', 200, 2, 'anonymous'),
    ('result-qualifiers/7a6a3957-f45f-4a00-9edf-d1e53a689538', 200, 2, 'alice'),
    ('result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 200, 2, 'anonymous'),
    ('result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 200, 2, 'alice'),
    ('result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 200, 2, 'bob'),
    ('result-qualifiers/00000000-0000-0000-0000-000000000000', 404, 2, 'anonymous'),
    ('result-qualifiers/72ce9a6d-3a8d-4a92-abb8-07924479193f', 404, 2, 'anonymous'),
    ('sensors/c45c6050-dc52-4a37-a562-66816a6ef1b5', 200, 2, 'anonymous'),
    ('sensors/c45c6050-dc52-4a37-a562-66816a6ef1b5', 200, 2, 'alice'),
    ('sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 200, 2, 'anonymous'),
    ('sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 200, 2, 'alice'),
    ('sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 200, 2, 'bob'),
    ('sensors/00000000-0000-0000-0000-000000000000', 404, 2, 'anonymous'),
    ('sensors/41ebe791-3868-4c09-9744-f6954d295edc', 404, 2, 'anonymous'),
    ('units/a1695fce-bbee-42eb-90da-44c951be7fbd', 200, 2, 'anonymous'),
    ('units/a1695fce-bbee-42eb-90da-44c951be7fbd', 200, 2, 'alice'),
    ('units/967944cb-903b-4f96-afba-3b9e69722f8f', 200, 2, 'anonymous'),
    ('units/967944cb-903b-4f96-afba-3b9e69722f8f', 200, 2, 'alice'),
    ('units/967944cb-903b-4f96-afba-3b9e69722f8f', 200, 2, 'bob'),
    ('units/00000000-0000-0000-0000-000000000000', 404, 2, 'anonymous'),
    ('units/20b29933-078d-48b9-95d2-d829ddecd5d8', 404, 2, 'anonymous'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 200, 2, 'alice'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 404, 2, 'bob'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 404, 2, 'anonymous'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 200, 2, 'alice'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 404, 2, 'bob'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 404, 2, 'anonymous'),
])
@pytest.mark.django_db()
def test_core_get_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, response_code, max_queries, user
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.get(
            f'{base_url}/{endpoint}',
            **auth_headers[user]
        )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, post_body, response_code, user', [
    ('things', {
        'latitude': 0, 'longitude': 0, 'elevation_m': 0, 'elevationDatum': 'string', 'state': 'string',
        'county': 'string', 'name': 'string', 'description': 'string', 'samplingFeatureType': 'string',
        'samplingFeatureCode': 'string', 'siteType': 'string', 'dataDisclaimer': 'string'
    }, 201, 'alice'),
    ('things', {}, 422, 'alice'),
    ('things', {}, 401, 'anonymous'),
    ('observed-properties', {
        'name': 'string', 'description': 'string', 'definition': 'string', 'type': 'string', 'code': 'string'
    }, 201, 'alice'),
    ('observed-properties', {}, 422, 'alice'),
    ('observed-properties', {}, 401, 'anonymous'),
    ('processing-levels', {
        'code': 'string', 'definition': 'string', 'explanation': 'string'
    }, 201, 'alice'),
    ('processing-levels', {}, 422, 'alice'),
    ('processing-levels', {}, 401, 'anonymous'),
    ('sensors', {
        'name': 'string', 'description': 'string', 'encodingType': 'string', 'methodType': 'string'
    }, 201, 'alice'),
    ('sensors', {}, 422, 'alice'),
    ('sensors', {}, 401, 'anonymous'),
    ('units', {
        'name': 'string', 'symbol': 'string', 'definition': 'string', 'type': 'string'
    }, 201, 'alice'),
    ('units', {}, 422, 'alice'),
    ('units', {}, 401, 'anonymous'),
    ('data-loaders', {
        'name': 'string'
    }, 201, 'alice'),
    ('data-loaders', {}, 422, 'alice'),
    ('data-loaders', {}, 401, 'anonymous'),
    ('data-sources', {
        'name': 'string', 'timestampColumn': 'string', 'dataLoaderId': '9d571b4b-c986-4fa8-8933-0491ddad9e0e',
        'paused': False
    }, 201, 'alice'),
    ('data-sources', {
        'name': 'string', 'timestampColumn': 'string', 'dataLoaderId': '9bcd1dbf-eb1e-47dd-8874-f0a65f16c709',
        'paused': False
    }, 403, 'alice'),
    ('data-sources', {}, 422, 'alice'),
    ('data-sources', {}, 401, 'anonymous'),
])
@pytest.mark.django_db()
def test_core_post_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, post_body, response_code, user
):
    client = Client()

    response = client.post(
        f'{base_url}/{endpoint}',
        json.dumps(post_body),
        content_type='application/json',
        **auth_headers[user]
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, patch_body, response_code, user', [
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1', {'description': 'A test thing.'}, 401, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1', {'description': 'A test thing.'}, 203, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1', {'description': 'A test thing.'}, 203, 'bob'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d', {'description': 'A test thing.'}, 404, 'bob'),
    ('observed-properties/11e37e36-3d65-497a-b432-e238ec45195b', {'name': 'Temperature'}, 404, 'alice'),
    ('observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', {'name': 'Temperature'}, 401, 'anonymous'),
    ('observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', {'name': 'Temperature'}, 203, 'alice'),
    ('processing-levels/caab642c-14f9-4823-8517-9b1bce59f626', {'definition': 'Raw'}, 404, 'alice'),
    ('processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', {'definition': 'Raw'}, 401, 'anonymous'),
    ('processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', {'definition': 'Raw'}, 203, 'alice'),
    ('result-qualifiers/7a6a3957-f45f-4a00-9edf-d1e53a689538', {'code': 'ICE'}, 404, 'alice'),
    ('result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', {'code': 'ICE'}, 401, 'anonymous'),
    ('result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', {'code': 'ICE'}, 203, 'alice'),
    ('sensors/c45c6050-dc52-4a37-a562-66816a6ef1b5', {'name': 'Sensor'}, 404, 'alice'),
    ('sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', {'name': 'Sensor'}, 401, 'anonymous'),
    ('sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', {'name': 'Sensor'}, 203, 'alice'),
    ('units/a1695fce-bbee-42eb-90da-44c951be7fbd', {'name': 'Celsius'}, 404, 'alice'),
    ('units/967944cb-903b-4f96-afba-3b9e69722f8f', {'name': 'Celsius'}, 401, 'anonymous'),
    ('units/967944cb-903b-4f96-afba-3b9e69722f8f', {'name': 'Celsius'}, 203, 'alice'),
    ('data-loaders/9bcd1dbf-eb1e-47dd-8874-f0a65f16c709', {'name': 'Alice\'s Streaming Data Loader'}, 404, 'alice'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', {'name': 'Alice\'s Streaming Data Loader'}, 401, 'anonymous'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', {'name': 'Alice\'s Streaming Data Loader'}, 203, 'alice'),
    ('data-sources/f47a257f-8007-4a5a-86e1-19bbd6093d9b', {'name': 'Test Data Source'}, 404, 'alice'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', {'name': 'Test Data Source'}, 401, 'anonymous'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', {'name': 'Test Data Source'}, 203, 'alice'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', {
        'dataLoaderId': '9d571b4b-c986-4fa8-8933-0491ddad9e0e'
    }, 203, 'alice'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', {
        'dataLoaderId': '9bcd1dbf-eb1e-47dd-8874-f0a65f16c709'
    }, 403, 'alice'),
])
@pytest.mark.django_db()
def test_core_patch_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, patch_body, response_code, user
):
    client = Client()

    response = client.patch(
        f'{base_url}/{endpoint}',
        json.dumps(patch_body),
        content_type='application/json',
        **auth_headers[user]
    )

    assert response.status_code == response_code
