from ninja import Router
from ninja_jwt.tokens import RefreshToken
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from hydroserver.auth import JWTAuth, BasicAuth
from accounts.models import Organization
from accounts.models.person import PasswordReset, account_verification_token
from accounts.schemas.person import (PersonGetResponse, PersonAuthResponse, PersonPostBody, PersonPatchBody,
                                     PasswordResetRequestPostBody, ResetPasswordPostBody, VerifyAccountPostBody)
from hydroserver import settings


person_router = Router(tags=['User Management'])
auth_router = Router(tags=['Basic Authentication'])
user_model = get_user_model()


@person_router.get(
    '/user',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: PersonGetResponse,
        401: str
    },
    by_alias=True
)
def get_user(request: HttpRequest):

    user = getattr(request, 'authenticated_user', None)
    if user and user.is_verified is False:
        user.email = user.unverified_email

    return user


if not settings.DISABLE_ACCOUNT_CREATION:
    @person_router.post(
        '/user',
        response={
            200: PersonAuthResponse,
            409: str, 422: str
        },
        by_alias=True
    )
    def create_user(request: HttpRequest, data: PersonPostBody):

        user = user_model.objects.filter(username=data.user_email, is_verified=True).first()

        if user:
            return 409, 'Email already linked to an existing account.'

        user = user_model.objects.create_user(
            email=data.user_email,
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

        user.send_verification_email()
        jwt = RefreshToken.for_user(user)

        user.email = user.unverified_email

        return 200, {
            'access': str(getattr(jwt, 'access_token', '')),
            'refresh': str(jwt),
            'user': user
        }


@person_router.patch(
    '/user',
    response={
        200: PersonGetResponse,  # TODO: Should update this to 203. Needs to be done on frontend as well.
        401: str, 403: str, 404: str, 422: str,
    },
    auth=[JWTAuth(), BasicAuth()],
    by_alias=True
)
def update_user(request: HttpRequest, data: PersonPatchBody):

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
        user.unverified_email = data.user_email
        user.send_verification_email()

    user.save()

    if user and user.is_verified is False:
        user.email = user.unverified_email

    return user


@person_router.delete(
    '/user',
    response={
        204: None,
        401:  str, 403: str, 404: str
    },
    auth=[JWTAuth(), BasicAuth()],
)
def delete_user(request: HttpRequest):

    user = getattr(request, 'authenticated_user', None)
    user.is_active = False
    user.save()

    return 204, None


if not settings.DISABLE_ACCOUNT_CREATION:
    @person_router.post(
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

        user.send_verification_email()

        return 200, 'Verification email sent.'


    @person_router.post(
        '/activate',
        response={
            403: str,
            200: PersonAuthResponse
        },
        by_alias=True
    )
    def activate_account(request: HttpRequest, data: VerifyAccountPostBody):
        user = user_model.objects.filter(
            username=data.uid,
            is_verified=False
        ).first()

        if user is None or user.is_verified is True:
            return 403, 'This account does not exist or has already been activated.'

        if account_verification_token.check_token(user, data.token):
            user = user.update_account_to_verified()
            jwt = RefreshToken.for_user(user)

            return 200, {
                'access': str(getattr(jwt, 'access_token', '')),
                'refresh': str(jwt),
                'user': user
            }

        else:
            return 403, 'Account activation token incorrect or expired.'


@person_router.post(
    '/send-password-reset-email',
    response={
        200: str,
        404: str,
        500: str
    }
)
def send_password_reset_email(
        request: HttpRequest,
        data: PasswordResetRequestPostBody
):
    try:
        user = user_model.objects.filter(email=data.email).filter(is_verified=True).filter(is_active=True).first()
        if user:
            try:
                password_reset = PasswordReset(user=user)
                password_reset.save()
            except IntegrityError:
                PasswordReset.objects.get(user=user).delete()
                password_reset = PasswordReset(user=user)
                password_reset.save()

            token = account_verification_token.make_token(user)
            user.send_password_reset_confirmation_email(password_reset.id, token)

            return 200, 'Password reset email sent.'
        else:
            return 404, 'User with the given email not found.'
    except Exception as e:
        return 500, str(e)


@person_router.post(
    '/reset-password',
    response={
        200: str,
        400: str
    }
)
def reset_password(
        request: HttpRequest,
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
