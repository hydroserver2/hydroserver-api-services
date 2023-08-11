import json
from ninja import Router
from ninja_jwt.tokens import RefreshToken
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


@orcid_router.get('/login')
def orcid_login(request):
    redirect_uri = request.build_absolute_uri('/auth/orcid/auth')

    if 'X-Forwarded-Proto' in request.headers:
        redirect_uri = redirect_uri.replace('http:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.orcid.authorize_redirect(request, redirect_uri)


@orcid_router.get('/auth')
def orcid_auth(request):
    token = oauth.orcid.authorize_access_token(request)

    print(token)


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
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(
            username=user_email,
            email=user_email,
            password='',
            first_name=token.get('userinfo', {}).get('given_name'),
            last_name=token.get('userinfo', {}).get('family_name'),
        )

    jwt_token = RefreshToken.for_user(user)

    response_html = '<html><head><title>HydroServer Sign In</title></head><body></body><script>res = %value%; ' + \
                    'window.opener.postMessage(res, "*");window.close();</script></html>'

    response_html = response_html.replace(
        "%value%", json.dumps({
            'access_token': str(getattr(jwt_token, 'access_token', '')),
            'refresh_token': str(jwt_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'middle_name': user.middle_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'address': user.address,
                'organization': user.organization,
                'type': user.type
            }
        })
    )

    return HttpResponse(response_html)
