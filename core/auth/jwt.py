from ninja import Router
from ninja.security import APIKeyHeader
from ninja_jwt.authentication import JWTBaseAuthentication
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from django.contrib.auth import get_user_model


api = NinjaExtraAPI(
    version='0.0.1',
    urls_namespace='jwt-auth'
)

api.register_controllers(NinjaJWTDefaultController)


class JWTAuth(APIKeyHeader, JWTBaseAuthentication):
    param_name = "X-API-Key"

    def authenticate(self, request, token):
        if not hasattr(self, 'user_model'):
            self.user_model = get_user_model()

        user = self.jwt_authenticate(request, token=token)

        if user and user.is_authenticated:
            request.authenticated_user = user
            return user
