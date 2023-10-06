import pytest
import base64
import json
from django.test import Client


@pytest.fixture
def auth_headers():
    return {
        'HTTP_AUTHORIZATION': 'Basic ' +
                              base64.b64encode(bytes('paul@example.com:thisispaulspassword', 'utf8')).decode('utf8'),
    }


@pytest.fixture
def base_url():
    return '/api/sensorthings/v1.1'


@pytest.mark.parametrize('endpoint, query_params', [
    ('Things', {}),
    ('Things(0c04fcdc-3876-429e-8260-14b7baca0231)/Datastreams', {}),
    ('Things(0c04fcdc-3876-429e-8260-14b7baca0231)/Locations', {}),
    ('Things', {'$count': True}),
    ('Things', {'$filter': 'name eq \'test\''}),
    ('Things', {'$skip': 10}),
    ('Things', {'$top': 10}),
    ('Things', {'$expand': 'Locations,Datastreams/Sensor'}),
    ('Locations', {}),
    ('Locations(e78380f8-bdb5-4f15-8f37-bde53a4dd5c3)/Things', {}),
    ('Locations(e78380f8-bdb5-4f15-8f37-bde53a4dd5c3)/HistoricalLocations', {}),
    ('Locations', {'$count': True}),
    ('Locations', {'$filter': 'name eq \'test\''}),
    ('Locations', {'$skip': 10}),
    ('Locations', {'$top': 10}),
    ('Locations', {'$expand': 'Things/Datastreams/ObservedProperty'}),
    ('HistoricalLocations', {}),
    ('HistoricalLocations', {'$count': True}),
    ('HistoricalLocations', {'$skip': 10}),
    ('HistoricalLocations', {'$top': 10}),
    ('Sensors', {}),
    ('Sensors(7294c8a8-a9d8-4490-b3be-315bbe971e0c)/Datastreams', {}),
    ('Sensors', {'$count': True}),
    ('Sensors', {'$filter': 'name eq \'test\''}),
    ('Sensors', {'$skip': 10}),
    ('Sensors', {'$top': 10}),
    ('Sensors', {'$expand': 'Datastreams/Thing'}),
    ('ObservedProperties', {}),
    ('ObservedProperties(4c310501-31f3-4954-80b0-2279eb049e39)/Datastreams', {}),
    ('ObservedProperties', {'$count': True}),
    ('ObservedProperties', {'$filter': 'name eq \'test\''}),
    ('ObservedProperties', {'$skip': 10}),
    ('ObservedProperties', {'$top': 10}),
    ('ObservedProperties', {'$expand': 'Datastreams/Thing'}),
    ('Datastreams', {}),
    ('Datastreams(8af17d0e-8fce-4264-93b5-e55aa6a7ca02)/Observations', {}),
    ('Datastreams', {'$count': True}),
    ('Datastreams', {'$filter': 'name eq \'ca999458-d644-44b0-b678-09a892fd54ac\''}),
    ('Datastreams', {'$skip': 10}),
    ('Datastreams', {'$top': 10}),
    ('Datastreams', {'$expand': 'Observations,Thing/Locations,Sensor,ObservedProperty'}),
    ('Observations', {}),
    ('Observations', {'$count': True}),
    ('Observations', {'$filter': 'result eq 10'}),
    ('Observations', {'$skip': 10}),
    ('Observations', {'$top': 10}),
    ('Observations', {'$resultFormat': 'dataArray'}),
    ('Observations', {'$expand': 'Datastream/Thing'}),
    ('FeaturesOfInterest', {}),
    ('FeaturesOfInterest', {'$count': True}),
    ('FeaturesOfInterest', {'$skip': 10}),
    ('FeaturesOfInterest', {'$top': 10}),
])
@pytest.mark.django_db()
def test_sensorthings_list_endpoints(django_test_db, auth_headers, base_url, endpoint, query_params):
    client = Client()

    response = client.get(
        f'{base_url}/{endpoint}',
        query_params,
        **auth_headers
    )
    json.loads(response.content)

    assert response.status_code == 200


@pytest.mark.parametrize('endpoint, query_params, status_code', [
    ('', {}, 200),
    ('Things(0c04fcdc-3876-429e-8260-14b7baca0231)', {}, 200),
    ('Things(0c04fcdc-3876-429e-8260-14b7baca0231)', {'$expand': 'Locations,Datastreams/Sensor'}, 200),
    ('Things(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('Locations(1796a56f-2cdf-42c6-8cc7-3da2f757e9a0)', {}, 200),
    ('Locations(1796a56f-2cdf-42c6-8cc7-3da2f757e9a0)', {'$expand': 'Things/Datastreams/ObservedProperty'}, 200),
    ('Locations(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('HistoricalLocations(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('Sensors(7294c8a8-a9d8-4490-b3be-315bbe971e0c)', {}, 200),
    ('Sensors(7294c8a8-a9d8-4490-b3be-315bbe971e0c)', {'$expand': 'Datastreams/Thing'}, 200),
    ('Sensors(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('ObservedProperties(97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19)', {}, 200),
    ('ObservedProperties(97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19)', {'$expand': 'Datastreams/Thing'}, 200),
    ('ObservedProperties(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('Datastreams(376be82c-b3a1-4d96-821b-c7954b931f94)', {}, 200),
    ('Datastreams(376be82c-b3a1-4d96-821b-c7954b931f94)', {
        '$expand': 'Observations,Thing/Locations,Sensor,ObservedProperty'
    }, 200),
    ('Datastreams(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('Datastreams(8af17d0e-8fce-4264-93b5-e55aa6a7ca02)/Sensor', {}, 200),
    ('Datastreams(8af17d0e-8fce-4264-93b5-e55aa6a7ca02)/ObservedProperty', {}, 200),
    ('Datastreams(8af17d0e-8fce-4264-93b5-e55aa6a7ca02)/Thing', {}, 200),
    ('Observations(71335328-fd9f-4079-b51d-ddd629545c27)', {}, 200),
    ('Observations(71335328-fd9f-4079-b51d-ddd629545c27)', {'$expand': 'Datastream/Thing'}, 200),
    ('Observations(00000000-0000-0000-0000-000000000000)', {}, 404),
    ('Observations(8119cba7-8c00-454d-9584-3f605b1a0c74)/Datastream', {}, 200),
    ('FeaturesOfInterest(00000000-0000-0000-0000-000000000000)', {}, 404),
])
@pytest.mark.django_db()
def test_sensorthings_get_endpoints(
        django_test_db,
        auth_headers,
        base_url,
        endpoint,
        query_params,
        status_code
):
    client = Client()

    response = client.get(
        f'{base_url}/{endpoint}',
        query_params,
        **auth_headers
    )
    json.loads(response.content)

    assert response.status_code == status_code


@pytest.mark.parametrize('endpoint, post_body, status_code', [
    ('Observations', {
        'phenomenonTime': '2023-10-01T10:00:00Z',
        'result': 23.2,
        'Datastream': {'@iot.id': '376be82c-b3a1-4d96-821b-c7954b931f94'}
    }, 201),
    ('Observations', [{
        'Datastream': {'@iot.id': '376be82c-b3a1-4d96-821b-c7954b931f94'},
        'engine': ['phenomenonTime', 'result'],
        'dataArray': [['2023-10-02T10:00:00Z', 24.5], ['2023-10-03T10:00:00Z', 22.8]]
    }], 201)
])
@pytest.mark.django_db()
def test_sensorthings_post_endpoints(
        django_test_db,
        auth_headers,
        base_url,
        endpoint,
        post_body,
        status_code
):
    client = Client()

    response = client.post(
        f'{base_url}/{endpoint}',
        json.dumps(post_body),
        content_type="application/json",
        **auth_headers
    )

    json.loads(response.content)

    assert response.status_code == status_code
