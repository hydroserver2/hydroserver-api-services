import pytest
import json
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/data'


@pytest.mark.parametrize('endpoint, query_params, response_code, response_length, max_queries', [
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8/datastreams', {}, 200, 1, 4),
    ('things/0c04fcdc-3876-429e-8260-14b7baca0231/datastreams', {}, 403, None, 4),
    ('things/00000000-0000-0000-0000-000000000000/datastreams', {}, 404, None, 4),
    ('datastreams', {}, 200, 2, 4),
    ('datastreams', {'modified_since': '2090-01-01T11:11:11Z'}, 200, 0, 4),
    ('datastreams', {'owned_only': True}, 200, 2, 4),
    ('datastreams', {'primary_owned_only': True}, 200, 1, 4),
    ('observed-properties', {}, 200, 3, 4),
    ('observed-properties', {'owned': True}, 200, 3, 4),
    ('observed-properties', {'owned': False}, 200, 0, 4),
    ('processing-levels', {}, 200, 3, 4),
    ('processing-levels', {'owned': True}, 200, 3, 4),
    ('processing-levels', {'owned': False}, 200, 0, 4),
    ('sensors', {}, 200, 3, 4),
    ('sensors', {'owned': True}, 200, 3, 4),
    ('sensors', {'owned': False}, 200, 0, 4),
    ('things', {'modified_since': '2090-01-01T11:11:11Z'}, 200, 0, 4),
    ('things', {'owned_only': True}, 200, 2, 4),
    ('things', {'primary_owned_only': True}, 200, 1, 4),
    ('units', {}, 200, 3, 4),
    ('units', {'owned': True}, 200, 3, 4),
    ('units', {'owned': False}, 200, 0, 4),
    ('result-qualifiers', {}, 200, 3, 4),
    ('result-qualifiers', {'owned': True}, 200, 3, 4),
    ('result-qualifiers', {'owned': False}, 200, 0, 4),
])
@pytest.mark.django_db()
def test_core_list_endpoints(
        django_assert_max_num_queries, django_jwt_auth, auth_headers, base_url, endpoint, query_params,
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
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8', 200, 5),
    ('things/0c04fcdc-3876-429e-8260-14b7baca0231', 403, 3),
    ('things/00000000-0000-0000-0000-000000000000', 404, 3),
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8/metadata', 200, 100),
    ('datastreams/ca999458-d644-44b0-b678-09a892fd54ac', 200, 5),
    ('datastreams/00000000-0000-0000-0000-000000000000', 404, 5),
])
@pytest.mark.django_db()
def test_core_get_endpoints(
        django_assert_max_num_queries, django_jwt_auth, auth_headers, base_url, endpoint, response_code,
        max_queries
):
    client = Client()

    with django_assert_max_num_queries(max_queries):
        response = client.get(
            f'{base_url}/{endpoint}',
            **auth_headers
        )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, post_body, response_code', [
    ('datastreams', {
        'thingId': '9344a3d4-a45a-4529-b731-b51149b4d1b8',
        'sensorId': '90d7f4a5-2042-4840-9bb4-b991f49cb8ed',
        'observedPropertyId': '97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19',
        'processingLevelId': '83fdb8ba-5db4-4f31-b1fa-e68478a4be13',
        'unitId': '52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9',
        'timeAggregationIntervalUnitsId': '52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9',
        'intendedTimeSpacingUnitsId': '52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9',
        'name': 'string',
        'description': 'string',
        'observationType': 'string',
        'sampledMedium': 'string',
        'noDataValue': 9999,
        'aggregationStatistic': 15,
        'timeAggregationInterval': 15,
        'status': 'string',
        'resultType': 'string',
        'valueCount': 0,
        'intendedTimeSpacing': 15,
    }, 201),
    ('datastreams', {}, 422),
    ('observed-properties', {
        'name': 'string',
        'definition': 'http://www.example.com',
        'description': 'string',
        'type': 'string',
        'code': 'string'
    }, 201),
    ('observed-properties', {}, 422),
    ('processing-levels', {
        'code': 'string',
        'definition': 'string',
        'explanation': 'string'
    }, 201),
    ('processing-levels', {}, 422),
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
    }, 201),
    ('sensors', {}, 422),
    ('result-qualifiers', {
        'code': 'string',
        'description': 'string'
    }, 201),
    ('result-qualifiers', {}, 422),
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
    }, 201),
    ('things', {}, 422),
    ('units', {
        'name': 'string',
        'symbol': 'string',
        'definition': 'string',
        'type': 'string'
    }, 201),
    ('units', {}, 422),
])
@pytest.mark.django_db()
def test_core_post_endpoints(
        django_assert_max_num_queries, django_jwt_auth, auth_headers, base_url, endpoint, post_body,
        response_code
):
    client = Client()

    response = client.post(
        f'{base_url}/{endpoint}',
        json.dumps(post_body),
        content_type='application/json',
        **auth_headers
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, patch_body, response_code', [
    ('datastreams/ca999458-d644-44b0-b678-09a892fd54ac', {'name': 'string'}, 203),
    ('observed-properties/97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19', {'name': 'string'}, 203),
    ('processing-levels/83fdb8ba-5db4-4f31-b1fa-e68478a4be13', {'code': 'string'}, 203),
    ('sensors/90d7f4a5-2042-4840-9bb4-b991f49cb8ed', {'name': 'string'}, 203),
    ('result-qualifiers/565b2407-fc55-4e4a-bcd7-6e945860f11b', {'code': 'string'}, 203),
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8', {'name': 'string'}, 203),
    ('things/0c04fcdc-3876-429e-8260-14b7baca0231', {'name': 'string'}, 403),
    ('things/00000000-0000-0000-0000-000000000000', {'name': 'string'}, 404),
    ('units/52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9', {'name': 'string'}, 203),
])
@pytest.mark.django_db()
def test_core_patch_endpoints(
        django_assert_max_num_queries, django_jwt_auth, auth_headers, base_url, endpoint, patch_body,
        response_code
):
    client = Client()

    response = client.patch(
        f'{base_url}/{endpoint}',
        json.dumps(patch_body),
        content_type='application/json',
        **auth_headers
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, response_code', [
    ('things/9344a3d4-a45a-4529-b731-b51149b4d1b8', 204),
    ('things/0c04fcdc-3876-429e-8260-14b7baca0231', 403),
    ('things/ab6d5d46-1ded-4ac6-8da8-0203df67950b', 204),
    ('things/00000000-0000-0000-0000-000000000000', 404),
    ('sensors/27fb4b01-478a-4ba8-a309-21ea49057704', 204),
    ('sensors/90d7f4a5-2042-4840-9bb4-b991f49cb8ed', 409),
    ('sensors/7294c8a8-a9d8-4490-b3be-315bbe971e0c', 403),
    ('sensors/00000000-0000-0000-0000-000000000000', 404),
    ('observed-properties/65d1d57a-528a-4a29-9a1e-a0e605eb6066', 204),
    ('observed-properties/97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19', 409),
    ('observed-properties/4c310501-31f3-4954-80b0-2279eb049e39', 403),
    ('observed-properties/00000000-0000-0000-0000-000000000000', 404),
    ('units/04d023bf-5d0a-4b61-9eac-7b7b6097af6f', 204),
    ('units/52eac9d0-72ab-4f0e-933d-8ad8b8a8a1f9', 409),
    ('units/d69bbc57-8c31-4f5a-8398-2aaea4bd1f5e', 403),
    ('units/00000000-0000-0000-0000-000000000000', 404),
    ('processing-levels/265f3951-7d73-4b7f-9b6a-ae19d3cecb2b', 204),
    ('processing-levels/83fdb8ba-5db4-4f31-b1fa-e68478a4be13', 409),
    ('processing-levels/7e57d004-2b97-44e7-8f03-713f25415a10', 403),
    ('processing-levels/00000000-0000-0000-0000-000000000000', 404),
    ('result-qualifiers/8dc7b570-0247-4ccf-a5f2-0831546571cf', 204),
    ('result-qualifiers/93ccb684-2921-49df-a6cf-2f0dea8eb210', 409),
    ('result-qualifiers/369c1e3e-e465-41bc-9b13-933d81d50d0d', 403),
    ('result-qualifiers/00000000-0000-0000-0000-000000000000', 404),
    ('datastreams/ca999458-d644-44b0-b678-09a892fd54ac', 204),
    ('datastreams/8af17d0e-8fce-4264-93b5-e55aa6a7ca02', 403),
    ('datastreams/376be82c-b3a1-4d96-821b-c7954b931f94', 403),
    ('datastreams/00000000-0000-0000-0000-000000000000', 404)
])
@pytest.mark.django_db()
def test_core_delete_endpoints(
        django_assert_max_num_queries, django_jwt_auth, auth_headers, base_url, endpoint, response_code
):
    client = Client()

    response = client.delete(
        f'{base_url}/{endpoint}',
        **auth_headers
    )

    assert response.status_code == response_code
