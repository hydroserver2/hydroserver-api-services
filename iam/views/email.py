from ninja import Router, Path
from typing import Literal
from allauth.headless.account.views import ManageEmailView, VerifyEmailView
from allauth.headless.constants import Client
from iam.schemas import VerificationEmailPutBody, VerifyEmailPostBody


email_router = Router(tags=["Email"])

email_view = {
    "browser": ManageEmailView.as_api_view(client=Client.BROWSER),
    "app": ManageEmailView.as_api_view(client=Client.APP)
}

verification_view = {
    "browser": VerifyEmailView.as_api_view(client=Client.BROWSER),
    "app": VerifyEmailView.as_api_view(client=Client.APP)
}


@email_router.put(
    "verify",
    response={
        200: str,
        400: str,
        401: str,
        409: str,
    },
    by_alias=True,
)
def send_verification_email(request, client: Path[Literal["browser", "app"]], body: VerificationEmailPutBody):
    """
    Send an account verification email.
    """

    response = email_view[client](request)

    return response


@email_router.post(
    "verify",
    response={
        200: str,
        400: str,
        401: str,
        409: str,
    },
    by_alias=True,
)
def verify_email(request, client: Path[Literal["browser", "app"]], body: VerifyEmailPostBody):
    """
    Verify an account email.
    """

    response = verification_view[client](request)

    return response
