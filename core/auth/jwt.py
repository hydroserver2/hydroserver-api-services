from ninja.security import APIKeyHeader
from ninja_extra import api_controller
from ninja_extra.permissions import AllowAny
from ninja_jwt.authentication import JWTBaseAuthentication
from ninja_jwt.controller import TokenVerificationController, TokenObtainPairController
from django.contrib.auth import get_user_model


@api_controller("/jwt", permissions=[AllowAny], tags=['JWT'])
class HydroServerJWTController(TokenVerificationController, TokenObtainPairController):

    auto_import = False


class JWTAuth(APIKeyHeader, JWTBaseAuthentication):
    param_name = "X-API-Key"

    def authenticate(self, request, token):
        if not hasattr(self, 'user_model'):
            self.user_model = get_user_model()

        user = self.jwt_authenticate(request, token=token)

        if user and user.is_authenticated:
            request.authenticated_user = user
            return user