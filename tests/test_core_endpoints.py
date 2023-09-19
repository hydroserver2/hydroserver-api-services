import pytest
import json
from django.test import Client


@pytest.fixture
def auth_headers(django_jwt_auth):
    return {
        'HTTP_AUTHORIZATION': 'Bearer ' + str(django_jwt_auth)
    }


@pytest.fixture
def base_url():
    return '/api/data'


@pytest.mark.parametrize('endpoint, query_params, response_code, response_length, max_queries', [
    # ('datastreams', {}, 200, 2, 100),
    # ('datastreams/9344a3d4-a45a-4529-b731-b51149b4d1b8', {}, 200, 1, 100),
    ('observed-properties', {}, 200, 1, 100),
    ('processing-levels', {}, 200, 1, 100),
    ('sensors', {}, 200, 1, 100),
    ('things', {}, 200, 3, 3),
    ('units', {}, 200, 1, 100)
])
@pytest.mark.django_db()
def test_core_list_endpoints(
        django_assert_max_num_queries, django_test_db, django_jwt_auth, auth_headers, base_url, endpoint, query_params,
        response_code, response_length, max_queries
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.get(
            f'{base_url}/{endpoint}',
            query_params,
            **auth_headers
        )

    assert response.status_code == response_code

    if response_length is not None:
        data = json.loads(response.content)
        assert len(data) == response_length


@pytest.mark.parametrize('endpoint, response_code, max_queries', [
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8', 200, 3),
    ('things/00000000-0000-0000-0000-000000000000', 404, 3),
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8/metadata', 200, 100),
])
@pytest.mark.django_db()
def test_core_get_endpoints(
        django_assert_max_num_queries, django_test_db, django_jwt_auth, auth_headers, base_url, endpoint, response_code,
        max_queries
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.get(
            f'{base_url}/{endpoint}',
            **auth_headers
        )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, post_body, response_code, max_queries', [
    # ('datastreams/9344a3d4-a45a-4529-b731-b51149b4d1b8', {
    #     'sensorId': '90d7f4a5-2042-4840-9bb4-b991f49cb8ed',
    #     'observedPropertyId': '97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19',
    #     'processingLevelId': '83fdb8ba-5db4-4f31-b1fa-e68478a4be13',
    #     'unitId': '52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9',
    #     'timeAggregationIntervalUnitsId': '52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9',
    #     'intendedTimeSpacingUnitsId': '52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9',
    #     'name': 'string',
    #     'description': 'string',
    #     'observationType': 'string',
    #     'sampledMedium': 'string',
    #     'noDataValue': 9999,
    #     'aggregationStatistic': 15,
    #     'timeAggregationInterval': 15,
    #     'status': 'string',
    #     'resultType': 'string',
    #     'valueCount': 0,
    #     'intendedTimeSpacing': 15,
    # }, 200, 100),
    # ('datastreams', {}, 422),
    ('observed-properties', {
        'name': 'string',
        'definition': 'string',
        'description': 'string',
        'type': 'string',
        'code': 'string'
    }, 201, 100),
    ('observed-properties', {}, 422, 100),
    ('processing-levels', {
        'code': 'string',
        'definition': 'string',
        'explanation': 'string'
    }, 201, 100),
    ('processing-levels', {}, 422, 100),
    ('sensors', {
        'name': 'string',
        'description': 'string',
        'encodingType': 'string',
        'manufacturer': 'string',
        'model': 'string',
        'modelLink': 'string',
        'methodType': 'string',
        'methodLink': 'string',
        'methodCode': 'string'
    }, 201, 100),
    ('sensors', {}, 422, 100),
    ('things', {
        'latitude': 0,
        'longitude': 0,
        'elevation_m': 0,
        'elevationDatum': 'string',
        'state': 'string',
        'county': 'string',
        'name': 'string',
        'description': 'string',
        'samplingFeatureType': 'string',
        'samplingFeatureCode': 'string',
        'siteType': 'string',
        'dataDisclaimer': 'string'
    }, 201, 8),
    ('things', {}, 422, 1),
    ('units', {
        'name': 'string',
        'symbol': 'string',
        'definition': 'string',
        'type': 'string'
    }, 201, 100),
    ('units', {}, 422, 100),
])
@pytest.mark.django_db()
def test_core_post_endpoints(
        django_assert_max_num_queries, django_test_db, django_jwt_auth, auth_headers, base_url, endpoint, post_body,
        response_code, max_queries
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.post(
            f'{base_url}/{endpoint}',
            json.dumps(post_body),
            content_type='application/json',
            **auth_headers
        )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, patch_body, response_code, max_queries', [
    # ('datastreams/patch/ca999458-d644-44b0-b678-09a892fd54ac', {'name': 'string'}, 203, 100),
    ('observed-properties/97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19', {'name': 'string'}, 203, 6),
    ('processing-levels/83fdb8ba-5db4-4f31-b1fa-e68478a4be13', {'code': 'string'}, 203, 6),
    ('sensors/90d7f4a5-2042-4840-9bb4-b991f49cb8ed', {'name': 'string'}, 203, 6),
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8', {'name': 'string'}, 203, 10),
    ('things/0c04fcdc-3876-429e-8260-14b7baca0231', {'name': 'string'}, 403, 6),
    ('things/00000000-0000-0000-0000-000000000000', {'name': 'string'}, 404, 6),
    ('units/52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9', {'name': 'string'}, 203, 6),
])
@pytest.mark.django_db()
def test_core_patch_endpoints(
        django_assert_max_num_queries, django_test_db, django_jwt_auth, auth_headers, base_url, endpoint, patch_body,
        response_code, max_queries
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.patch(
            f'{base_url}/{endpoint}',
            json.dumps(patch_body),
            content_type='application/json',
            **auth_headers
        )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, response_code, max_queries', [
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8', 204, 15),
    ('things/0c04fcdc-3876-429e-8260-14b7baca0231', 403, 6),
    ('things/ab6d5d46-1ded-4ac6-8da8-0203df67950b', 403, 6),
    ('things/00000000-0000-0000-0000-000000000000', 404, 6)
])
@pytest.mark.django_db()
def test_core_delete_endpoints(
        django_assert_max_num_queries, django_test_db, django_jwt_auth, auth_headers, base_url, endpoint, response_code,
        max_queries
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.delete(
            f'{base_url}/{endpoint}',
            **auth_headers
        )

    assert response.status_code == response_code
