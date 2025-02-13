from ninja import Router, Path
from typing import Literal
from allauth.headless.account.views import SignupView
from allauth.headless.constants import Client
from iam.schemas import AccountGetResponse, AccountPostBody, AccountPatchBody, TypeGetResponse
from iam.services import AccountService
from hydroserver.security import anonymous_auth, bearer_auth, session_auth
from hydroserver.http import HydroServerHttpRequest

account_router = Router(tags=["Account"])
account_service = AccountService()

signup_view = {
    "browser": SignupView.as_api_view(client=Client.BROWSER),
    "app": SignupView.as_api_view(client=Client.APP)
}


@account_router.get(
    "",
    auth=[session_auth, bearer_auth],
    response={
        200: AccountGetResponse,
        401: str,
    },
    by_alias=True
)
def get_account(request: HydroServerHttpRequest, client: Path[Literal["browser", "app"]]):
    """
    Get user account details.
    """

    return 200, account_service.get(user=request.authenticated_user)


@account_router.post(
    "",
    url_name="signup",
    response={
        200: AccountGetResponse,
        400: str,
        401: str,
        403: str,
        409: str,
        422: str,
    },
    by_alias=True
)
def create_account(request, client: Path[Literal["browser", "app"]], data: AccountPostBody):
    """
    Create a new user account.
    """

    response = signup_view[client](request)

    return response


@account_router.patch(
    "",
    auth=[session_auth, bearer_auth],
    response={
        200: AccountGetResponse,
        401: str,
        422: str
    },
    by_alias=True
)
def update_account(request: HydroServerHttpRequest, client: Path[Literal["browser", "app"]], data: AccountPatchBody):
    """
    Update user account details.
    """

    return 200, account_service.update(
        user=request.authenticated_user,
        data=data
    )


@account_router.delete(
    "",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str
    }
)
def delete_account(request: HydroServerHttpRequest, client: Path[Literal["browser", "app"]]):
    """
    Delete a user account.
    """

    return 204, account_service.delete(
        user=request.authenticated_user,
    )


@account_router.get(
    "/types",
    auth=[anonymous_auth],
    response={
        200: TypeGetResponse
    },
    by_alias=True
)
def get_types(request, client: Path[Literal["browser", "app"]]):
    """
    Get allowed user and organization types.
    """

    return 200, account_service.get_types()
