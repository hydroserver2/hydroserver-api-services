from ninja import Router, Query
from ninja_jwt.tokens import RefreshToken
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from accounts.schemas import *
from accounts.utils import account_activation_token, update_account_to_verified
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
    """"""

    user = getattr(request, 'authenticated_user', None)

    if user and user.is_verified is False:
        user.email = user.unverified_email

    return user


@user_router.post('/user')
def create_user(_: HttpRequest, data: UserPostBody):
    """"""

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

    jwt = RefreshToken.for_user(user)

    return {
        'access_token': str(jwt),
        'refresh_token': str(getattr(jwt, 'access_token', '')),
        'uid': base64.b64encode(user.username.encode('ascii')).decode('ascii')
    }


@user_router.patch('/user')
def update_user(request: HttpRequest):
    """"""

    print(request.user.first_name)

    pass


@user_router.post('/send-verification-email')
def send_verification_email(_: HttpRequest, data: UserVerificationPostBody):
    """"""

    user = user_model.objects.filter(username=data.uid, is_verified=False).first()

    if not user:
        return None

    context = {
        'uid': base64.b64encode(data.uid.encode('ascii')).decode('ascii'),
        'token': account_activation_token.make_token(user),
        'name': user.first_name,
        'proxy_base_url': settings.PROXY_BASE_URL
    }

    html_message = render_to_string('verify_account_email.html', context)

    send_mail(
        'Verify HydroServer Account',
        '',  # Don't support plain text emails
        'HydroServer <admin@hydroserver.ciroh.org>',
        [user.unverified_email],
        html_message=html_message,
    )

    return None


@user_router.get('/verify-account')
def verify_account(_: HttpRequest, params: UserVerificationConfirmationParams = Query(...)):
    """"""

    user = user_model.objects.filter(username=params.uid, is_verified=False).first()

    if user is not None and account_activation_token.check_token(user, params.token):
        update_account_to_verified(user)
