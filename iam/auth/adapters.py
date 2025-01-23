from typing import Dict, Any
from django.http import HttpRequest
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import get_adapter as get_account_adapter
from iam.schemas import ProfileGetResponse, ProfilePatchBody


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


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        user.set_unusable_password()

        if form:
            data = form.cleaned_data
            user = get_account_adapter().save_user(request, user, form, commit=False)
            profile = ProfilePatchBody(
                **{
                    "middle_name": data.get("middle_name") or None,
                    "phone": data.get("phone") or None,
                    "address": data.get("address") or None,
                    "link": data.get("link") or None,
                    "user_type": data.get("user_type") or None,
                    "organization": data.get("organization") or None,
                }
            )
            profile.save(user)

        else:
            get_account_adapter().populate_username(request, user)

        sociallogin.save(request)

        return user
