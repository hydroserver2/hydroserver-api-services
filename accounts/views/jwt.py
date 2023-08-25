from ninja_extra import api_controller
from ninja_extra.permissions import AllowAny
from ninja_jwt.controller import TokenVerificationController, TokenObtainPairController


@api_controller('/jwt', permissions=[AllowAny], tags=['JWT Authentication'])
class HydroServerJWTController(TokenVerificationController, TokenObtainPairController):

    auto_import = False
