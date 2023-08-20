from ninja.security import HttpBearer
from ninja_jwt.authentication import JWTBaseAuthentication
from django.contrib.auth import get_user_model


class JWTAuth(JWTBaseAuthentication, HttpBearer):
    def authenticate(self, request, token):

        if not hasattr(self, 'user_model'):
            self.user_model = get_user_model()

        user = self.jwt_authenticate(request, token=token)

        if user and user.is_authenticated:
            request.authenticated_user = user
            return user
