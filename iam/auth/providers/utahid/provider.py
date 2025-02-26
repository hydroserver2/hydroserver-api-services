from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from iam.auth.providers.utahid.views import UtahIdOAuth2Adapter


class UtahIdAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get("name", super().to_str())


class UtahIdProvider(OAuth2Provider):
    id = "utahid"
    name = "UtahID"
    account_class = UtahIdAccount
    oauth2_adapter_class = UtahIdOAuth2Adapter

    def get_default_scope(self):
        return ["openid", "email", "profile"]

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            last_name=data.get("family_name"),
            first_name=data.get("given_name"),
        )


provider_classes = [UtahIdProvider]
