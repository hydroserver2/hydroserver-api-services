import pytest
import json
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/data'


@pytest.mark.parametrize('endpoint, query_params, response_code, response_length, max_queries, user', [
    ('things', {}, 200, 2, 3, 'anonymous'),
    ('things', {}, 200, 5, 4, 'alice'),
    ('things', {'modified_since': '2090-01-01T11:11:11Z'}, 200, 0, 3, 'anonymous'),
    ('things', {'owned_only': True}, 200, 3, 4, 'bob'),
    ('things', {'owned_only': True}, 200, 0, 4, 'anonymous'),
    ('things', {'primary_owned_only': True}, 200, 5, 4, 'alice'),
    ('things', {'primary_owned_only': True}, 200, 0, 4, 'anonymous'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/metadata', {}, 200, 4, 6, 'anonymous'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/datastreams', {}, 200, 3, 4, 'anonymous'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/datastreams', {}, 200, 4, 4, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', {}, 200, 2, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', {}, 200, 2, 4, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', {}, 200, 2, 4, 'carol'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags', {}, 200, 1, 4, 'alice'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags', {}, 404, 1, 4, 'anonymous'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags', {}, 404, 1, 4, 'carol'),
    ('things/00000000-0000-0000-0000-000000000000/tags', {}, 404, 1, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', {}, 200, 2, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', {}, 200, 2, 4, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', {}, 200, 2, 4, 'carol'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', {}, 200, 1, 4, 'alice'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', {}, 404, 1, 4, 'anonymous'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', {}, 404, 1, 4, 'carol'),
    ('things/00000000-0000-0000-0000-000000000000/photos', {}, 404, 1, 4, 'anonymous'),
    ('observed-properties', {}, 200, 4, 3, 'anonymous'),
    ('observed-properties', {}, 200, 4, 3, 'alice'),
    ('observed-properties', {'owner': 'currentUser'}, 200, 2, 3, 'alice'),
    ('observed-properties', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('observed-properties', {'owner': 'currentUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('observed-properties', {'owner': 'anyUser'}, 200, 3, 3, 'alice'),
    ('observed-properties', {'owner': 'anyUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('processing-levels', {}, 200, 4, 3, 'anonymous'),
    ('processing-levels', {}, 200, 4, 3, 'alice'),
    ('processing-levels', {'owner': 'currentUser'}, 200, 2, 3, 'alice'),
    ('processing-levels', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('processing-levels', {'owner': 'currentUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('processing-levels', {'owner': 'anyUser'}, 200, 3, 3, 'alice'),
    ('processing-levels', {'owner': 'anyUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('result-qualifiers', {}, 200, 5, 3, 'anonymous'),
    ('result-qualifiers', {}, 200, 5, 3, 'alice'),
    ('result-qualifiers', {'owner': 'currentUser'}, 200, 3, 3, 'alice'),
    ('result-qualifiers', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('result-qualifiers', {'owner': 'currentUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('result-qualifiers', {'owner': 'anyUser'}, 200, 4, 3, 'alice'),
    ('result-qualifiers', {'owner': 'anyUserOrNoUser'}, 200, 5, 3, 'alice'),
    ('sensors', {}, 200, 4, 3, 'anonymous'),
    ('sensors', {}, 200, 4, 3, 'alice'),
    ('sensors', {'owner': 'currentUser'}, 200, 2, 3, 'alice'),
    ('sensors', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('sensors', {'owner': 'currentUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('sensors', {'owner': 'anyUser'}, 200, 3, 3, 'alice'),
    ('sensors', {'owner': 'anyUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('units', {}, 200, 4, 3, 'anonymous'),
    ('units', {}, 200, 4, 3, 'alice'),
    ('units', {'owner': 'currentUser'}, 200, 2, 3, 'alice'),
    ('units', {'owner': 'noUser'}, 200, 1, 3, 'alice'),
    ('units', {'owner': 'currentUserOrNoUser'}, 200, 3, 3, 'alice'),
    ('units', {'owner': 'anyUser'}, 200, 3, 3, 'alice'),
    ('units', {'owner': 'anyUserOrNoUser'}, 200, 4, 3, 'alice'),
    ('data-loaders', {}, 200, 0, 3, 'anonymous'),
    ('data-loaders', {}, 200, 2, 3, 'alice'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', {}, 404, 1, 3, 'anonymous'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', {}, 404, 1, 3, 'bob'),
    ('data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', {}, 200, 2, 3, 'alice'),
    ('data-sources', {}, 200, 0, 3, 'anonymous'),
    ('data-sources', {}, 200, 2, 3, 'alice'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717/datastreams', {}, 404, 1, 3, 'anonymous'),
    ('data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717/datastreams', {}, 200, 2, 3, 'alice'),
    ('datastreams', {}, 200, 3, 3, 'anonymous'),
    ('datastreams', {}, 200, 7, 3, 'alice'),
    ('datastreams', {}, 200, 4, 3, 'bob'),
    ('datastreams', {'modified_since': '2090-01-01T11:11:11Z'}, 200, 0, 3, 'anonymous'),
    ('datastreams', {'owned_only': True}, 200, 1, 4, 'bob'),
    ('datastreams', {'owned_only': True}, 200, 0, 4, 'anonymous'),
    ('datastreams', {'primary_owned_only': True}, 200, 7, 4, 'alice'),
    ('datastreams', {'primary_owned_only': True}, 200, 0, 4, 'anonymous'),
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
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 200, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 200, 4, 'alice'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags/fb2db25f-0cf2-4bc6-ab15-282d924d2790', 200, 4, 'alice'),
    ('things/00000000-0000-0000-0000-000000000000/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 404, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/00000000-0000-0000-0000-000000000000', 404, 4, 'anonymous'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags/fb2db25f-0cf2-4bc6-ab15-282d924d2790', 404, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos/ada2c09b-27d7-4b57-87d4-a859c6d9368f', 200, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos/ada2c09b-27d7-4b57-87d4-a859c6d9368f', 200, 4, 'alice'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos/c74bf8cb-5855-49e6-97c9-546d2e8bc07f', 200, 4, 'alice'),
    ('things/00000000-0000-0000-0000-000000000000/photos/ada2c09b-27d7-4b57-87d4-a859c6d9368f', 404, 4, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos/00000000-0000-0000-0000-000000000000', 404, 4, 'anonymous'),
    ('things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos/c74bf8cb-5855-49e6-97c9-546d2e8bc07f', 404, 4, 'anonymous'),
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
    ('datastreams/bf5542df-5500-45b4-aabc-4835534880ff', 200, 4, 'anonymous'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 404, 4, 'anonymous'),
    ('datastreams/00000000-0000-0000-0000-000000000000', 404, 4, 'anonymous'),
    ('datastreams/61895e0e-5395-489e-845b-562d5b93db22', 404, 4, 'anonymous'),
    ('datastreams/3a028176-ee60-47cc-a573-222dbfbe6b34', 404, 4, 'anonymous'),
    ('datastreams/fd22da23-2291-4c14-bcbc-9fdb4671b2cb', 200, 4, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 200, 4, 'bob'),
    ('datastreams/1b98de60-0386-4d98-a933-b3cd0c09d98e', 404, 4, 'bob'),
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
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', {
        'key': 'string', 'value': 'string'
    }, 201, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', {}, 422, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', {}, 401, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', {}, 422, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', {}, 401, 'anonymous'),
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
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
        'timeAggregationIntervalUnits': 'minutes'
    }, 201, 'alice'),
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
        'timeAggregationIntervalUnits': 'minutes'
    }, 201, 'bob'),
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '76dadda5-224b-4e1f-8570-e385bd482b2d', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
        'timeAggregationIntervalUnits': 'minutes'
    }, 404, 'bob'),
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': '5fbab69a-810b-4044-bfac-c40a05634c5c',
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
        'timeAggregationIntervalUnits': 'minutes'
    }, 403, 'bob'),
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
        'observedPropertyId': 'c1479bbc-3d7e-449c-ad3a-0a1c7742b460',
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
        'timeAggregationIntervalUnits': 'minutes'
    }, 403, 'bob'),
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
        'processingLevelId': 'fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
        'timeAggregationIntervalUnits': 'minutes'
    }, 403, 'bob'),
    ('datastreams', {
        'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
        'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '054ac53a-520f-4340-96f1-889ffa12874b',
        'timeAggregationIntervalUnits': 'minutes'
    }, 403, 'bob'),
    ('datastreams', {}, 422, 'alice'),
    ('datastreams', {}, 401, 'anonymous'),
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
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', {
        'key': 'Code'
    }, 401, 'anonymous'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', {
        'key': 'Code'
    }, 203, 'alice'),
    ('things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', {
        'key': 'Code'
    }, 404, 'carol'),
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
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {'name': 'TSC Temperature'}, 203, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1'
    }, 203, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1'
    }, 203, 'bob'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'thingId': '5bba0397-096b-4d60-a3f0-c00f1e6e85da'
    }, 403, 'bob'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c'
    }, 203, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'sensorId': '5fbab69a-810b-4044-bfac-c40a05634c5c'
    }, 403, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f'
    }, 203, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'processingLevelId': 'fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd'
    }, 403, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb'
    }, 203, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'observedPropertyId': 'c1479bbc-3d7e-449c-ad3a-0a1c7742b460'
    }, 403, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f'
    }, 203, 'alice'),
    ('datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', {
        'unitId': '054ac53a-520f-4340-96f1-889ffa12874b'
    }, 403, 'alice'),
    ('datastreams/1b98de60-0386-4d98-a933-b3cd0c09d98e', {'name': 'TSC Temperature'}, 404, 'bob'),
    ('datastreams/1b98de60-0386-4d98-a933-b3cd0c09d98e', {'name': 'TSC Temperature'}, 401, 'anonymous'),
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


@pytest.mark.parametrize('endpoint, response_code, user', [
    ('things/e1f18e11-4130-485b-ad67-18f7f44187f8', 401, 'anonymous'),
    ('things/e1f18e11-4130-485b-ad67-18f7f44187f8', 404, 'carol'),
    ('things/e1f18e11-4130-485b-ad67-18f7f44187f8', 404, 'bob'),
    ('things/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('things/e1f18e11-4130-485b-ad67-18f7f44187f8', 204, 'alice'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 401, 'anonymous'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 404, 'carol'),
    ('things/00000000-0000-0000-0000-000000000000/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 404, 'alice'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 204, 'alice'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/photos/a6360259-ba57-414d-84ab-22b5c64eb78d', 401, 'anonymous'),
    ('things/76dadda5-224b-4e1f-8570-e385bd482b2d/photos/a6360259-ba57-414d-84ab-22b5c64eb78d', 404, 'carol'),
    ('things/00000000-0000-0000-0000-000000000000/photos/a6360259-ba57-414d-84ab-22b5c64eb78d', 404, 'alice'),
    ('observed-properties/2f89ca87-667f-4de9-b850-715db3cbf927', 401, 'anonymous'),
    ('observed-properties/2f89ca87-667f-4de9-b850-715db3cbf927', 404, 'carol'),
    ('observed-properties/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('observed-properties/2f89ca87-667f-4de9-b850-715db3cbf927', 204, 'alice'),
    ('processing-levels/57d48dd3-0fc7-4127-8e34-99c4441c7b68', 401, 'anonymous'),
    ('processing-levels/57d48dd3-0fc7-4127-8e34-99c4441c7b68', 404, 'carol'),
    ('processing-levels/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('processing-levels/57d48dd3-0fc7-4127-8e34-99c4441c7b68', 204, 'alice'),
    ('result-qualifiers/3064f342-f614-41a7-8748-246a711e5175', 401, 'anonymous'),
    ('result-qualifiers/3064f342-f614-41a7-8748-246a711e5175', 404, 'carol'),
    ('result-qualifiers/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('result-qualifiers/3064f342-f614-41a7-8748-246a711e5175', 204, 'alice'),
    ('sensors/a8617070-146a-4e82-8b4d-9a6563de6265', 401, 'anonymous'),
    ('sensors/a8617070-146a-4e82-8b4d-9a6563de6265', 404, 'carol'),
    ('sensors/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('sensors/a8617070-146a-4e82-8b4d-9a6563de6265', 204, 'alice'),
    ('units/23bd903d-36f2-4572-b2e2-fd0a55c00498', 401, 'anonymous'),
    ('units/23bd903d-36f2-4572-b2e2-fd0a55c00498', 404, 'carol'),
    ('units/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('units/23bd903d-36f2-4572-b2e2-fd0a55c00498', 204, 'alice'),
    ('data-loaders/eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd', 401, 'anonymous'),
    ('data-loaders/eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd', 404, 'carol'),
    ('data-loaders/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('data-loaders/eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd', 204, 'alice'),
    ('data-sources/91783bce-b13a-42f7-ab22-4282c6303c42', 401, 'anonymous'),
    ('data-sources/91783bce-b13a-42f7-ab22-4282c6303c42', 404, 'carol'),
    ('data-sources/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('data-sources/91783bce-b13a-42f7-ab22-4282c6303c42', 204, 'alice'),
    ('datastreams/22074b3e-455a-4a4b-91c3-38e6cf85557d', 401, 'anonymous'),
    ('datastreams/22074b3e-455a-4a4b-91c3-38e6cf85557d', 404, 'carol'),
    ('datastreams/00000000-0000-0000-0000-000000000000', 404, 'alice'),
    ('datastreams/22074b3e-455a-4a4b-91c3-38e6cf85557d', 204, 'alice')
])
@pytest.mark.django_db()
def test_core_delete_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, response_code, user
):
    client = Client()

    response = client.delete(
        f'{base_url}/{endpoint}',
        **auth_headers[user]
    )

    assert response.status_code == response_code
