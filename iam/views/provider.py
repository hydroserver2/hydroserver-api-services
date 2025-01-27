from ninja import Router, Path, Form
from typing import Literal
from allauth.headless.socialaccount.views import RedirectToProviderView, ProviderSignupView
from allauth.headless.constants import Client
from iam.schemas import ProviderRedirectPostForm, AccountPostBody


provider_router = Router(tags=["Provider"])

provider_redirect_view = {
    "browser": RedirectToProviderView.as_api_view(client=Client.BROWSER),
    "app": RedirectToProviderView.as_api_view(client=Client.APP)
}

provider_signup_view = {
    "browser": ProviderSignupView.as_api_view(client=Client.BROWSER),
    "app": ProviderSignupView.as_api_view(client=Client.APP)
}


@provider_router.post(
    "redirect",
    url_name="redirect_to_provider",
    response={
        302: None,
    },
    by_alias=True
)
def redirect_to_provider(request, client: Path[Literal["browser", "app"]], form: Form[ProviderRedirectPostForm]):
    """
    Redirect to provider login window.
    """

    response = provider_redirect_view[client](request)

    return response


@provider_router.post(
    "signup",
    url_name="provider_signup",
    response={
        200: str,
        400: str,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True
)
def provider_signup(request, client: Path[Literal["browser", "app"]], body: AccountPostBody):
    """
    Finish signing up with a provider account.
    """

    response = provider_signup_view[client](request)

    return response
