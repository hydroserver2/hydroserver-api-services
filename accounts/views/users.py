from ninja import Router
from ninja_jwt.tokens import RefreshToken
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from accounts.schemas import *
from accounts.utils import account_activation_token, update_account_to_verified, send_verification_email
from accounts.auth import JWTAuth, BasicAuth


user_router = Router(tags=['User Management'])
auth_router = Router(tags=['Basic Authentication'])
user_model = get_user_model()


@user_router.get(
    '/user',
    auth=[BasicAuth(), JWTAuth()],
    response=UserGetResponse
)
def get_user(request: HttpRequest):

    user = getattr(request, 'authenticated_user', None)

    if user and user.is_verified is False:
        user.email = user.unverified_email

    return user


@user_router.post('/user')
def create_user(_: HttpRequest, data: UserPostBody):

    user = user_model.objects.filter(username=data.email, is_verified=True).first()

    if user:
        return None

    user = user_model.objects.create_user(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name,
        organization=data.organization,
        type=data.type,
        phone=data.phone,
        address=data.address
    )

    send_verification_email(user)
    jwt = RefreshToken.for_user(user)

    return {
        'access_token': str(jwt),
        'refresh_token': str(getattr(jwt, 'access_token', '')),
    }


@user_router.patch('/user')
def update_user(request: HttpRequest):

    print(request.user.first_name)

    pass


@user_router.post(
    '/send-verification-email',
    auth=JWTAuth(),
    response={
        403: str,
        200: str
    }
)
def verify_account(request: HttpRequest):

    user = getattr(request, 'authenticated_user', None)

    if not user or user.is_verified is not False:
        return 403, 'Email address has already been verified for this account.'

    send_verification_email(user)

    return 200, 'Verification email sent.'


@user_router.post(
    '/activate',
    response={
        403: str,
        200: UserGetResponse
    }
)
def activate_account(_: HttpRequest, data: VerifyAccountPostBody):

    user = user_model.objects.filter(
        username=data.uid,
        is_verified=False
    ).first()

    if user is None or user.is_verified is True:
        return 403, 'This account does not exist or has already been activated.'

    if account_activation_token.check_token(user, data.token):
        user = update_account_to_verified(user)
        return 200, user
    else:
        return 403, 'Account activation token incorrect or expired.'
