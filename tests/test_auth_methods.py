# import pytest
# from django.contrib.auth import get_user_model
# from django.test import RequestFactory
# from ninja.errors import HttpError
# from accounts.auth import BasicAuth
# from accounts.auth.backends import UnverifiedUserBackend
# from accounts.auth.anonymous import anonymous_auth
# from accounts.models import Person
#
#
# # backends.py
#
# @pytest.fixture
# def unverified_user():
#     user = get_user_model().objects.create_user(
#         email='test@example.com',
#         password='password123',
#         is_verified=False
#     )
#     return user
#
#
# @pytest.mark.django_db
# def test_unverified_user_authentication(unverified_user):
#     backend = UnverifiedUserBackend()
#     request = RequestFactory().post('/login/')
#     authenticated_user = backend.authenticate(request, email='test@example.com', password='password123')
#     assert authenticated_user == unverified_user
#
#
# @pytest.mark.django_db
# def test_unverified_user_authentication_invalid_credentials(unverified_user):
#     backend = UnverifiedUserBackend()
#     request = RequestFactory().post('/login/')
#     authenticated_user = backend.authenticate(request, email='test@example.com', password='wrongpassword')
#     assert authenticated_user is None
#
#
# @pytest.mark.django_db
# def test_get_user(unverified_user):
#     backend = UnverifiedUserBackend()
#     user = backend.get_user(user_id=unverified_user.id)
#     assert user == unverified_user
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
# @pytest.fixture
# def authenticated_user():
#     user = Person.objects.create_user(email='test@example.com', password='password123')
#     return user
#
#
# @pytest.mark.django_db
# def test_basic_auth_success(authenticated_user):
#     auth = BasicAuth()
#     request = RequestFactory().get('/')
#     user = auth.authenticate(request, username='test@example.com', password='password123')
#     assert user == authenticated_user
#     assert request.authenticated_user == authenticated_user
#
#
# @pytest.mark.django_db
# def test_basic_auth_invalid_credentials():
#     auth = BasicAuth()
#     request = RequestFactory().get('/')
#     with pytest.raises(HttpError) as exc_info:
#         auth.authenticate(request, username='invalid@example.com', password='invalid_password')
#     assert exc_info.value.status_code == 401
#
#
# @pytest.mark.django_db
# def test_basic_auth_inactive_user(authenticated_user):
#     authenticated_user.is_active = False
#     authenticated_user.save()
#     auth = BasicAuth()
#     request = RequestFactory().get('/')
#     with pytest.raises(HttpError) as exc_info:
#         auth.authenticate(request, username='test@example.com', password='password123')
#     assert exc_info.value.status_code == 401
