from ninja.security import HttpBearer
from ninja_jwt.authentication import JWTBaseAuthentication
from ninja_jwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth import get_user_model


class JWTAuth(JWTBaseAuthentication, HttpBearer):
    def authenticate(self, request, token, *args, **kwargs):

        if not hasattr(self, 'user_model'):
            self.user_model = get_user_model()

        try:
            user = self.jwt_authenticate(request, token=token)
        except (InvalidToken, AuthenticationFailed):
            user = None

        if user and user.is_authenticated:
            request.authenticated_user = user
            return user
