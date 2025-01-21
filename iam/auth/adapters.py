from typing import Dict, Any
from django.http import HttpRequest
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.headless.adapter import DefaultHeadlessAdapter
from iam.schemas import ProfileGetResponse


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return settings.ACCOUNT_SIGNUP_ENABLED


class HeadlessAdapter(DefaultHeadlessAdapter):
    def serialize_user(self, user) -> Dict[str, Any]:
        """
        Attaches user profile metadata to AllAuth responses.
        """

        user_response = super().serialize_user(user=user)
        user_profile = ProfileGetResponse.from_orm(user)
        user_response["profile"] = user_profile.dict(by_alias=True)

        return user_response
