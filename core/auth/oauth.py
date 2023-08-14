import json
from typing import Optional
from ninja import Router
from django.contrib.auth import login
from django.http import HttpResponse
from authlib.integrations.django_client import OAuth
from accounts.models import CustomUser
from hydroserver import settings


oauth = OAuth()

oauth.register(
    name='orcid',
    server_metadata_url=settings.AUTHLIB_OAUTH_CLIENTS['orcid']['server_metadata_url'],
    client_kwargs={'scope': 'openid email profile'}
)

orcid_router = Router(tags=['ORCID'])


def oauth_response(
        user: Optional[CustomUser] = None,
        user_info: Optional[dict] = None,
        finish_account_setup: Optional[bool] = False):
    """"""

    if not user_info:
        user_info = {}

    response_html = '<html><head><title>HydroServer Sign In</title></head><body></body><script>res = %value%; ' + \
                    'window.opener.postMessage(res, "*");window.close();</script></html>'

    response_html = response_html.replace(
        "%value%", json.dumps({
            'finish_account_setup': finish_account_setup,
            'user': {
                'email': getattr(user, 'email', user_info.get('email')),
                'first_name': getattr(user, 'first_name', user_info.get('first_name')),
                'middle_name': getattr(user, 'middle_name', None),
                'last_name': getattr(user, 'last_name', user_info.get('last_name')),
                'phone': getattr(user, 'phone', None),
                'address': getattr(user, 'address', None),
                'organization': getattr(user, 'organization', None),
                'type': getattr(user, 'type', None),
            }
        })
    )

    return response_html


@orcid_router.get('/login')
def orcid_login(request):
    redirect_uri = request.build_absolute_uri('/api2/auth/orcid/auth')

    if 'X-Forwarded-Proto' in request.headers:
        redirect_uri = redirect_uri.replace('http:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.orcid.authorize_redirect(request, redirect_uri)


@orcid_router.get('/auth')
def orcid_auth(request):

    token = oauth.orcid.authorize_access_token(request)
    user_id = token.get('userinfo', {}).get('sub')

    # try:
    #     user = CustomUser.objects.get(orcid=user_id)
    # except CustomUser.DoesNotExist:
    #     user = CustomUser.objects.create(
    #         username=user_id,
    #         orcid=user_id,
    #         password='',
    #         first_name=token.get('userinfo', {}).get('given_name'),
    #         last_name=token.get('userinfo', {}).get('family_name'),
    #     )
    #
    # return oauth_response(user)

    return None


oauth.register(
    name='google',
    server_metadata_url=settings.AUTHLIB_OAUTH_CLIENTS['google']['server_metadata_url'],
    client_kwargs={'scope': 'openid email profile'}
)

google_router = Router(tags=['Google'])


@google_router.get('/login')
def google_login(request):
    redirect_uri = request.build_absolute_uri('/api2/auth/google/auth')

    if 'X-Forwarded-Proto' in request.headers:
        redirect_uri = redirect_uri.replace('http:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.google.authorize_redirect(request, redirect_uri)


@google_router.get('/auth')
def google_auth(request):

    token = oauth.google.authorize_access_token(request)
    user_email = token.get('userinfo', {}).get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
        login(request, user)

        response = oauth_response(
            finish_account_setup=False,
            user=user
        )

    except CustomUser.DoesNotExist:
        response = oauth_response(
            finish_account_setup=True,
            user_info={
                'email': user_email,
                'first_name': token.get('userinfo', {}).get('given_name'),
                'last_name': token.get('userinfo', {}).get('family_name')
            }
        )

    return HttpResponse(response)
