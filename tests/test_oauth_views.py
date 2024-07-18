import pytest


@pytest.mark.parametrize('endpoint, response_code', [
    ('/api/account/google/login', 302),
])
@pytest.mark.django_db()
def test_google_endpoints(client, endpoint, response_code):
    response = client.get(endpoint)
    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, response_code', [
    ('/api/account/hydroshare/login', 302),
])
@pytest.mark.django_db()
def test_google_endpoints(client, endpoint, response_code):
    response = client.get(endpoint)
    assert response.status_code == response_code


@pytest.mark.parametrize('endpoint, response_code', [
    ('/api/account/orcid/login', 302),
])
@pytest.mark.django_db()
def test_google_endpoints(client, endpoint, response_code):
    response = client.get(endpoint)
    assert response.status_code == response_code
