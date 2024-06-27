# import pytest
# from django.test import RequestFactory
# from ninja.errors import HttpError
# from hydroserver.auth import BasicAuth, anonymous_auth
# from hydroserver.backends import UnverifiedUserBackend
#
#
# # backends.py
#
# @pytest.mark.django_db
# def test_unverified_user_authentication():
#     backend = UnverifiedUserBackend()
#     request = RequestFactory().post('/login/')
#     authenticated_user = backend.authenticate(request, email='dave@example.com', password='dave')
#     assert authenticated_user.first_name == 'Dave'
#
#
# @pytest.mark.django_db
# def test_unverified_user_authentication_invalid_credentials():
#     backend = UnverifiedUserBackend()
#     request = RequestFactory().post('/login/')
#     authenticated_user = backend.authenticate(request, email='dave@example.com', password='wrongpassword')
#     assert authenticated_user is None
#
#
# @pytest.mark.django_db
# def test_get_user():
#     backend = UnverifiedUserBackend()
#     user = backend.get_user(user_id=1000000013)
#     assert user.first_name == 'Dave'
#
#
# @pytest.mark.django_db
# def test_get_user_invalid_id():
#     backend = UnverifiedUserBackend()
#     user = backend.get_user(user_id=999)
#     assert user is None
#
#
# # anonymous.py
#
# @pytest.mark.django_db
# def test_anonymous_auth():
#     request = RequestFactory().get('/')
#     result = anonymous_auth(request)
#     assert result is True
#     assert request.authenticated_user is None
#
#
# # basic.py
#
# @pytest.mark.django_db
# def test_basic_auth_success():
#     auth = BasicAuth()
#     request = RequestFactory().get('/')
#     user = auth.authenticate(request, username='alice@example.com', password='alice')
#     assert user.first_name == 'Alice'
#     assert request.authenticated_user.first_name == 'Alice'
#
#
# @pytest.mark.django_db
# def test_basic_auth_invalid_credentials():
#     auth = BasicAuth()
#     request = RequestFactory().get('/')
#     with pytest.raises(HttpError) as exc_info:
#         auth.authenticate(request, username='alice@example.com', password='invalid_password')
#     assert exc_info.value.status_code == 401
#
#
# @pytest.mark.django_db
# def test_basic_auth_inactive_user():
#     auth = BasicAuth()
#     request = RequestFactory().get('/')
#     with pytest.raises(HttpError) as exc_info:
#         auth.authenticate(request, username='emily@example.com', password='emily')
#     assert exc_info.value.status_code == 401
