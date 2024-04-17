import pytest
import json
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/sensorthings/v1.1'


@pytest.mark.parametrize('endpoint, query_params, user', [
    ('Things', {}, 'anonymous'),
    ('Things(\'3b7818af-eff7-4149-8517-e5cad9dc22e1\')/Datastreams', {}, 'anonymous'),
    ('Things(\'3b7818af-eff7-4149-8517-e5cad9dc22e1\')/Locations', {}, 'anonymous'),
    ('Things', {'$count': True}, 'anonymous'),
    ('Things', {'$filter': 'name eq \'test\''}, 'anonymous'),
    ('Things', {'$skip': 10}, 'anonymous'),
    ('Things', {'$top': 10}, 'anonymous'),
    ('Things', {'$expand': 'Locations,Datastreams/Sensor'}, 'anonymous'),
    ('Locations', {}, 'anonymous'),
    ('Locations(\'8a6f1578-060a-40d9-9064-f8c4af4da80d\')/Things', {}, 'anonymous'),
    ('Locations(\'8a6f1578-060a-40d9-9064-f8c4af4da80d\')/HistoricalLocations', {}, 'anonymous'),
    ('Locations', {'$count': True}, 'anonymous'),
    ('Locations', {'$filter': 'name eq \'test\''}, 'anonymous'),
    ('Locations', {'$skip': 10}, 'anonymous'),
    ('Locations', {'$top': 10}, 'anonymous'),
    ('Locations', {'$expand': 'Things/Datastreams/ObservedProperty'}, 'anonymous'),
    ('HistoricalLocations', {}, 'anonymous'),
    ('HistoricalLocations', {'$count': True}, 'anonymous'),
    ('HistoricalLocations', {'$skip': 10}, 'anonymous'),
    ('HistoricalLocations', {'$top': 10}, 'anonymous'),
    ('Sensors', {}, 'anonymous'),
    ('Sensors(\'a9e79b5a-ae38-4314-abb0-604ee8d6049c\')/Datastreams', {}, 'anonymous'),
    ('Sensors', {'$count': True}, 'anonymous'),
    ('Sensors', {'$filter': 'name eq \'test\''}, 'anonymous'),
    ('Sensors', {'$skip': 10}, 'anonymous'),
    ('Sensors', {'$top': 10}, 'anonymous'),
    ('Sensors', {'$expand': 'Datastreams/Thing'}, 'anonymous'),
    ('ObservedProperties', {}, 'anonymous'),
    ('ObservedProperties(\'cda18a59-3f2c-4c09-976f-3eadc34423bb\')/Datastreams', {}, 'anonymous'),
    ('ObservedProperties', {'$count': True}, 'anonymous'),
    ('ObservedProperties', {'$filter': 'name eq \'test\''}, 'anonymous'),
    ('ObservedProperties', {'$skip': 10}, 'anonymous'),
    ('ObservedProperties', {'$top': 10}, 'anonymous'),
    ('ObservedProperties', {'$expand': 'Datastreams/Thing'}, 'anonymous'),
    ('Datastreams', {}, 'anonymous'),
    ('Datastreams(\'bf5542df-5500-45b4-aabc-4835534880ff\')/Observations', {}, 'anonymous'),
    ('Datastreams', {'$count': True}, 'anonymous'),
    ('Datastreams', {'$filter': 'name eq \'ca999458-d644-44b0-b678-09a892fd54ac\''}, 'anonymous'),
    ('Datastreams', {'$skip': 10}, 'anonymous'),
    ('Datastreams', {'$top': 10}, 'anonymous'),
    ('Datastreams', {'$expand': 'Observations,Thing/Locations,Sensor,ObservedProperty'}, 'anonymous'),
    ('Observations', {}, 'anonymous'),
    ('Observations', {'$count': True}, 'anonymous'),
    ('Observations', {'$filter': 'result eq 10'}, 'anonymous'),
    ('Observations', {'$skip': 10}, 'anonymous'),
    ('Observations', {'$top': 10}, 'anonymous'),
    ('Observations', {'$resultFormat': 'dataArray'}, 'anonymous'),
    ('Observations', {'$expand': 'Datastream/Thing'}, 'anonymous'),
    ('FeaturesOfInterest', {}, 'anonymous'),
    ('FeaturesOfInterest', {'$count': True}, 'anonymous'),
    ('FeaturesOfInterest', {'$skip': 10}, 'anonymous'),
    ('FeaturesOfInterest', {'$top': 10}, 'anonymous'),
])
@pytest.mark.django_db()
def test_sensorthings_list_endpoints(auth_headers, base_url, endpoint, query_params, user):
    client = Client()

    response = client.get(
        f'{base_url}/{endpoint}',
        query_params,
        **auth_headers[user]
    )
    json.loads(response.content)

    assert response.status_code == 200


@pytest.mark.parametrize('endpoint, query_params, status_code, user', [
    ('', {}, 200, 'anonymous'),
    ('Things(\'3b7818af-eff7-4149-8517-e5cad9dc22e1\')', {}, 200, 'anonymous'),
    ('Things(\'3b7818af-eff7-4149-8517-e5cad9dc22e1\')', {'$expand': 'Locations,Datastreams/Sensor'}, 200, 'anonymous'),
    ('Things(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
    ('Locations(\'8a6f1578-060a-40d9-9064-f8c4af4da80d\')', {}, 200, 'anonymous'),
    ('Locations(\'8a6f1578-060a-40d9-9064-f8c4af4da80d\')', {
        '$expand': 'Things/Datastreams/ObservedProperty'
    }, 200, 'anonymous'),
    ('Locations(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
    ('HistoricalLocations(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
    ('Sensors(\'a9e79b5a-ae38-4314-abb0-604ee8d6049c\')', {}, 200, 'anonymous'),
    ('Sensors(\'a9e79b5a-ae38-4314-abb0-604ee8d6049c\')', {'$expand': 'Datastreams/Thing'}, 200, 'anonymous'),
    ('Sensors(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
    ('ObservedProperties(\'cda18a59-3f2c-4c09-976f-3eadc34423bb\')', {}, 200, 'anonymous'),
    ('ObservedProperties(\'cda18a59-3f2c-4c09-976f-3eadc34423bb\')', {
        '$expand': 'Datastreams/Thing'
    }, 200, 'anonymous'),
    ('ObservedProperties(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
    ('Datastreams(\'bf5542df-5500-45b4-aabc-4835534880ff\')', {}, 200, 'anonymous'),
    ('Datastreams(\'bf5542df-5500-45b4-aabc-4835534880ff\')', {
        '$expand': 'Observations,Thing/Locations,Sensor,ObservedProperty'
    }, 200, 'anonymous'),
    ('Datastreams(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
    ('Datastreams(\'bf5542df-5500-45b4-aabc-4835534880ff\')/Sensor', {}, 200, 'anonymous'),
    ('Datastreams(\'bf5542df-5500-45b4-aabc-4835534880ff\')/ObservedProperty', {}, 200, 'anonymous'),
    ('Datastreams(\'bf5542df-5500-45b4-aabc-4835534880ff\')/Thing', {}, 200, 'anonymous'),
    ('Observations(\'d4e7aa38-0403-437d-958d-849b55cfa015\')', {}, 200, 'anonymous'),
    ('Observations(\'d4e7aa38-0403-437d-958d-849b55cfa015\')', {'$expand': 'Datastream/Thing'}, 200, 'anonymous'),
    ('Observations(\'176fe316-90cf-4ecd-9c9f-25ed5e3a2da9\')', {}, 404, 'anonymous'),
    ('Observations(\'d4e7aa38-0403-437d-958d-849b55cfa015\')/Datastream', {}, 200, 'anonymous'),
    ('FeaturesOfInterest(\'00000000-0000-0000-0000-000000000000\')', {}, 404, 'anonymous'),
])
@pytest.mark.django_db()
def test_sensorthings_get_endpoints(
        auth_headers,
        base_url,
        endpoint,
        query_params,
        status_code,
        user
):
    client = Client()

    response = client.get(
        f'{base_url}/{endpoint}',
        query_params,
        **auth_headers[user]
    )
    json.loads(response.content)

    assert response.status_code == status_code


@pytest.mark.parametrize('endpoint, post_body, status_code, user', [
    ('Observations', {
        'phenomenonTime': '2023-10-01T10:00:00Z',
        'result': 23.2,
        'Datastream': {'@iot.id': 'bf5542df-5500-45b4-aabc-4835534880ff'}
    }, 201, 'alice'),
    ('CreateObservations', [{
        'Datastream': {'@iot.id': 'bf5542df-5500-45b4-aabc-4835534880ff'},
        'components': ['phenomenonTime', 'result'],
        'dataArray': [['2023-10-02T10:00:00Z', 24.5], ['2023-10-03T10:00:00Z', 22.8]]
    }], 201, 'alice')
])
@pytest.mark.django_db()
def test_sensorthings_post_endpoints(
        auth_headers,
        base_url,
        endpoint,
        post_body,
        status_code,
        user
):
    client = Client()

    response = client.post(
        f'{base_url}/{endpoint}',
        json.dumps(post_body),
        content_type="application/json",
        **auth_headers[user]
    )

    json.loads(response.content)

    assert response.status_code == status_code
