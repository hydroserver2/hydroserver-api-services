import pytest
import base64
import json
from django.test import Client


@pytest.fixture
def auth_headers():
    return {
        'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(bytes('paul@example.com:default', 'utf8')).decode('utf8'),
    }


@pytest.fixture
def base_url():
    return '/sensorthings/v1.1'


@pytest.mark.parametrize('endpoint, query_params', [
    ('Things', {}),
    ('Things', {'$count': True}),
    ('Things', {'$filter': 'name eq \'test\''}),
    ('Things', {'$skip': 10}),
    ('Things', {'$top': 10}),
    ('Things', {'$expand': 'Locations,Datastreams/Sensor'}),
    ('Locations', {}),
    ('Locations', {'$count': True}),
    ('Locations', {'$filter': 'name eq \'test\''}),
    ('Locations', {'$skip': 10}),
    ('Locations', {'$top': 10}),
    ('Locations', {'$expand': 'Things/Datastreams/ObservedProperty'}),
    ('HistoricalLocations', {}),
    ('HistoricalLocations', {'$count': True}),
    # ('HistoricalLocations', {'$filter': 'name eq \'test\''}),
    ('HistoricalLocations', {'$skip': 10}),
    ('HistoricalLocations', {'$top': 10}),
    ('Sensors', {}),
    ('Sensors', {'$count': True}),
    ('Sensors', {'$filter': 'name eq \'test\''}),
    ('Sensors', {'$skip': 10}),
    ('Sensors', {'$top': 10}),
    ('Sensors', {'$expand': 'Datastreams/Thing'}),
    ('ObservedProperties', {}),
    ('ObservedProperties', {'$count': True}),
    ('ObservedProperties', {'$filter': 'name eq \'test\''}),
    ('ObservedProperties', {'$skip': 10}),
    ('ObservedProperties', {'$top': 10}),
    ('ObservedProperties', {'$expand': 'Datastreams/Thing'}),
    ('Datastreams', {}),
    ('Datastreams', {'$count': True}),
    ('Datastreams', {'$filter': 'name eq \'test\''}),
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
    # ('FeaturesOfInterest', {'$filter': 'name eq \'test\''}),
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


@pytest.mark.parametrize('endpoint, entity_id, query_params, status_code', [
    ('Things', '0c04fcdc-3876-429e-8260-14b7baca0231', {}, 200),
    ('Things', '0c04fcdc-3876-429e-8260-14b7baca0231', {'$expand': 'Locations,Datastreams/Sensor'}, 200),
    ('Things', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('Locations', '0c04fcdc-3876-429e-8260-14b7baca0231', {}, 200),
    ('Locations', '0c04fcdc-3876-429e-8260-14b7baca0231', {'$expand': 'Things/Datastreams/ObservedProperty'}, 200),
    ('Locations', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('HistoricalLocations', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('Sensors', '7294c8a8-a9d8-4490-b3be-315bbe971e0c', {}, 200),
    ('Sensors', '7294c8a8-a9d8-4490-b3be-315bbe971e0c', {'$expand': 'Datastreams/Thing'}, 200),
    ('Sensors', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('ObservedProperties', '97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19', {}, 200),
    ('ObservedProperties', '97f5e0b8-e1e9-4c65-9b98-0438cdfb4a19', {'$expand': 'Datastreams/Thing'}, 200),
    ('ObservedProperties', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('Datastreams', '376be82c-b3a1-4d96-821b-c7954b931f94', {}, 200),
    ('Datastreams', '376be82c-b3a1-4d96-821b-c7954b931f94', {
        '$expand': 'Observations,Thing/Locations,Sensor,ObservedProperty'
    }, 200),
    ('Datastreams', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('Observations', '6e45fc87-25ab-4e8a-965f-83014c0ad8fd', {}, 200),
    ('Observations', '6e45fc87-25ab-4e8a-965f-83014c0ad8fd', {'$expand': 'Datastream/Thing'}, 200),
    ('Observations', '00000000-0000-0000-0000-000000000000', {}, 404),
    ('FeaturesOfInterest', '00000000-0000-0000-0000-000000000000', {}, 404),
])
@pytest.mark.django_db()
def test_sensorthings_get_endpoints(
        django_test_db,
        auth_headers,
        base_url,
        endpoint,
        entity_id,
        query_params,
        status_code
):
    client = Client()

    response = client.get(
        f'{base_url}/{endpoint}({entity_id})',
        query_params,
        **auth_headers
    )
    json.loads(response.content)

    assert response.status_code == status_code
