from ninja import Router
from ninja_jwt.tokens import RefreshToken
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from accounts.schemas import *
from accounts.utils import account_verification_token, update_account_to_verified, send_verification_email
from accounts.auth import JWTAuth, BasicAuth
from accounts.models import PasswordReset


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


@user_router.post('/user', response=UserAuthResponse)
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
        address=data.address,
        link=data.link
    )

    send_verification_email(user)
    jwt = RefreshToken.for_user(user)

    user.email = user.unverified_email

    return {
        'access': str(jwt),
        'refresh': str(getattr(jwt, 'access_token', '')),
        'user': user
    }


@user_router.patch('/user', response=UserGetResponse, auth=JWTAuth())
def update_user(request: HttpRequest, data: UserPatchBody):

    user = getattr(request, 'authenticated_user', None)
    user_data = data.dict(exclude_unset=True)

    for field in ['first_name', 'last_name', 'middle_name', 'phone', 'address', 'organization', 'type', 'link']:
        if field in user_data:
            setattr(user, field, getattr(data, field))

    if 'email' in user_data and user.unverified_email is None:
        user.unverified_email = data.email
        send_verification_email(user)

    if user and user.is_verified is False:
        user.email = user.unverified_email

    user.save()

    return user


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
        200: UserAuthResponse
    }
)
def activate_account(_: HttpRequest, data: VerifyAccountPostBody):

    user = user_model.objects.filter(
        username=data.uid,
        is_verified=False
    ).first()

    if user is None or user.is_verified is True:
        return 403, 'This account does not exist or has already been activated.'

    if account_verification_token.check_token(user, data.token):
        user = update_account_to_verified(user)
        jwt = RefreshToken.for_user(user)

        return {
            'access': str(jwt),
            'refresh': str(getattr(jwt, 'access_token', '')),
            'user': user
        }

    else:
        return 403, 'Account activation token incorrect or expired.'


@user_router.post(
    '/send-password-reset-email',
    response={
        200: str,
        404: str,
        500: str
    }
)
def send_password_reset_email(
        _: HttpRequest,
        data: PasswordResetRequestPostBody
):
    try:
        user = user_model.objects.filter(email=data.email).first()
        if user:
            try:
                password_reset = PasswordReset(user=user)
                password_reset.save()
            except IntegrityError:
                PasswordReset.objects.get(user=user).delete()
                password_reset = PasswordReset(user=user)
                password_reset.save()

            token = account_verification_token.make_token(user)
            send_password_reset_email(user, password_reset.id, token)

            return 200, 'Password reset email sent.'
        else:
            return 404, 'User does not exist'
    except Exception as e:
        return 500, str(e)


@user_router.post(
    '/reset-password',
    response={
        200: str,
        400: str
    }
)
def reset_password(
        _: HttpRequest,
        data: ResetPasswordPostBody
):
    try:
        password_reset = PasswordReset.objects.get(pk=data.uid)
    except PasswordReset.DoesNotExist:
        return 400, 'Invalid UID'

    user = password_reset.user

    if not account_verification_token.check_token(user, data.token):
        return 400, 'Invalid or expired token'

    user.set_password(data.password)
    user.save()
    password_reset.delete()

    return 200, 'Password reset successful'
