from ninja import Router
from ninja_jwt.tokens import RefreshToken
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from accounts.schemas import *
from accounts.utils import account_verification_token, update_account_to_verified, send_verification_email, \
     send_password_reset_confirmation_email, build_user_response
from accounts.auth import JWTAuth, BasicAuth
from accounts.models import PasswordReset, Organization


user_router = Router(tags=['User Management'])
auth_router = Router(tags=['Basic Authentication'])
user_model = get_user_model()


@user_router.get(
    '/user',
    auth=[JWTAuth(), BasicAuth()],
    response=UserGetResponse, 
    by_alias=True
)
def get_user(request: HttpRequest):

    user = getattr(request, 'authenticated_user', None)
    if user and user.is_verified is False:
        user.email = user.unverified_email

    return build_user_response(user)


@user_router.post(
    '/user',
        response={
        409: str,
        200: UserAuthResponse
    },
    by_alias=True
)
def create_user(_: HttpRequest, data: UserPostBody):

    user = user_model.objects.filter(username=data.email, is_verified=True).first()

    if user:
        return 409, 'Email already linked to an existing account.'

    user = user_model.objects.create_user(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name,
        type=data.type,
        phone=data.phone,
        address=data.address,
        link=data.link
    )

    if getattr(data, 'organization', None) is not None:
        Organization.objects.create(person=user, **data.organization.dict())

    send_verification_email(user)
    jwt = RefreshToken.for_user(user)

    user.email = user.unverified_email

    return 200, {
        'access': str(getattr(jwt, 'access_token', '')),
        'refresh': str(jwt),
        'user': build_user_response(user)
    }


@user_router.patch(
    '/user',
    response=UserGetResponse,
    auth=JWTAuth(),
    by_alias=True
)
def update_user(request: HttpRequest, data: UserPatchBody):

    user = getattr(request, 'authenticated_user', None)
    included_names = {'first_name', 'last_name', 'middle_name', 'phone', 'address', 'type', 'link'}
    user_data = data.dict(include=included_names, exclude_unset=True)

    for field in user_data:
        setattr(user, field, getattr(data, field))

    org_data = data.organization

    if 'organization' in data.dict(exclude_unset=True):
        if not org_data and user.organization:
            user.organization.delete()
            user.organization = None
        elif org_data:
            if user.organization:
                for field, value in org_data.dict(exclude_unset=True).items():
                    setattr(user.organization, field, value)
                user.organization.save()
            else:
                user.organization = Organization.objects.create(**org_data.dict())

    if 'email' in data.dict(exclude_unset=True) and user.is_verified is False:
        user.unverified_email = data.email
        send_verification_email(user)

    user.save()

    return build_user_response(user)


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
    },
    by_alias=True
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

        return 200, {
            'access': str(getattr(jwt, 'access_token', '')),
            'refresh': str(jwt),
            'user': build_user_response(user)
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
            send_password_reset_confirmation_email(user, password_reset.id, token)

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
