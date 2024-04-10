# import pytest
# from ninja.errors import HttpError
# from ninja_jwt.tokens import RefreshToken
# from django.test import RequestFactory
# from django.contrib.auth.hashers import make_password
# from accounts.auth.jwt import JWTAuth
# from accounts.auth.basic import BasicAuth
# from accounts.auth.anonymous import anonymous_auth
# from accounts.models import Person
#
#
# @pytest.fixture
# def request_factory():
#     return RequestFactory()
#
#
# @pytest.fixture
# def jwt_auth():
#     return JWTAuth()
#
#
# @pytest.fixture
# def basic_auth():
#     return BasicAuth()
#
#
# @pytest.mark.django_db
# @pytest.fixture(scope='module')
# def users(django_db_setup, django_db_blocker):
#     del django_db_setup
#     with django_db_blocker.unblock():
#         Person.objects.create(
#             username="user1@example.com",
#             email="user1@example.com",
#             password=make_password("pass"),
#             is_verified=True
#         ),
#         Person.objects.create(
#             username="user2_token@example.com",
#             unverified_email="user2@example.com",
#             email="user2_token@hydroserver.org",
#             password=make_password("pass"),
#             is_verified=False
#         ),
#         Person.objects.create(
#             username="user3_token@example.com",
#             unverified_email="user3@example.com",
#             email="user3_token@hydroserver.org",
#             password=make_password("pass"),
#             is_verified=False
#         ),
#         Person.objects.create(
#             username="user3@example.com",
#             email="user3@hydroserver.org",
#             password=make_password("pass"),
#             is_verified=True
#         ),
#         Person.objects.create(
#             username="user4_token@example.com",
#             email="user4_token@hydroserver.org",
#             password=make_password("pass"),
#             is_verified=False
#         ),
#         yield
#
#
# @pytest.mark.parametrize('username, password, valid', [
#     ("user1@example.com", "pass", True),
#     ("user1@example.com", "wrong", False),
#     ("user2@example.com", "pass", True),
#     ("user2@example.com", "wrong", False),
#     ("user2_token@example.com", "pass", False),
#     ("user3@example.com", "pass", True),
#     ("user4@example.com", "pass", False),
#     ("user4_token@example.com", "pass", False),
#     ("user5@example.com", "pass", False),
# ])
# def test_basic_auth(request_factory, users, basic_auth, username, password, valid):
#     request = request_factory.get("/")
#
#     if not valid:
#         with pytest.raises(HttpError):
#             basic_auth.authenticate(request, username, password)
#     else:
#         basic_auth.authenticate(request, username, password)
#
#         assert hasattr(request, 'authenticated_user')
#
#         if request.authenticated_user.is_verified is True:
#             assert request.authenticated_user.email == username
#         else:
#             assert request.authenticated_user.unverified_email == username
#
#
# @pytest.mark.parametrize('username, token, valid', [
#     ("user1@example.com", "12345", False),
# ])
# def test_jwt_auth(request_factory, users, jwt_auth, username, token, valid):
#     request = request_factory.get("/")
#
#     if not token:
#         user = Person.objects.get(email=username)
#         refresh = RefreshToken.for_user(user)
#         token = getattr(refresh, 'access_token')
#
#     if not valid:
#         with pytest.raises(HttpError):
#             jwt_auth.authenticate(request, token)
#     else:
#         jwt_auth.authenticate(request, token)
#
#         assert hasattr(request, 'authenticated_user')
#         assert request.authenticated_user.email == username
#
#
# def test_anonymous_auth(request_factory):
#     request = request_factory.get("/")
#     anonymous_auth(request)
#
#     assert hasattr(request, 'authenticated_user')
#     assert request.authenticated_user is None
