import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from .views import HydroShareOAuth2Adapter


class Scope:
    EMAIL = "email"
    PROFILE = "profile"


class HydroShareAccount(ProviderAccount):
    """
    """

    pass

    # def get_profile_url(self):
    #     return self.account.extra_data.get("link")
    #
    # def get_avatar_url(self):
    #     return self.account.extra_data.get("picture")


class HydroShareProvider(OAuth2Provider):
    id = "hydroshare"
    name = "HydroShare"
    account_class = HydroShareAccount
    oauth2_adapter_class = HydroShareOAuth2Adapter
    supports_token_authentication = True

    def get_default_scope(self):
        scope = [Scope.PROFILE]
        if QUERY_EMAIL:
            scope.append(Scope.EMAIL)
        return scope

    def get_auth_params_from_request(self, request, action):
        ret = super().get_auth_params_from_request(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret["prompt"] = "select_account consent"
        return ret

    def extract_uid(self, data):
        if "sub" in data:
            return data["sub"]
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            last_name=data.get("family_name"),
            first_name=data.get("given_name"),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            verified = bool(data.get("email_verified") or data.get("verified_email"))
            ret.append(EmailAddress(email=email, verified=verified, primary=True))
        return ret

    def verify_token(self, request, token):
        from allauth.socialaccount.providers.google import views

        credential = token.get("id_token")
        if not credential:
            raise get_adapter().validation_error("invalid_token")
        try:
            identity_data = views._verify_and_decode(
                app=self.app, credential=credential
            )
        except (OAuth2Error, requests.RequestException) as e:
            raise get_adapter().validation_error("invalid_token") from e
        login = self.sociallogin_from_response(request, identity_data)
        return login


provider_classes = [HydroShareProvider]
