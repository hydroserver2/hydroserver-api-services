from ninja import Router
from ninja_jwt.tokens import RefreshToken
from hydroserver import settings
from django.shortcuts import redirect
from accounts.views.oauth.client import oauth, user_model
from accounts.utils import update_account_to_verified

oauth.register(
    name='google',
    server_metadata_url=settings.AUTHLIB_OAUTH_CLIENTS['google']['server_metadata_url'],
    client_kwargs={'scope': 'openid email profile'}
)

google_router = Router(tags=['Google OAuth 2.0'])


@google_router.get('/login')
def google_login(request):
    if settings.DEPLOYED is True:
        redirect_uri = f'{settings.PROXY_BASE_URL}/api/account/google/auth'
    else:
        redirect_uri = request.build_absolute_uri('/api/account/google/auth')

    # TODO: There's an issue with AWS that's causing the X-Forwarded-Proto header to always be set to http.
    # if 'X-Forwarded-Proto' in request.headers:
    #     redirect_uri = redirect_uri.replace('https:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.google.authorize_redirect(request, redirect_uri)


@google_router.get('/auth')
def google_auth(request):
    token = oauth.google.authorize_access_token(request)
    user_email = token.get('userinfo', {}).get('email')

    try:
        user = user_model.objects.get(email=user_email)

    except user_model.DoesNotExist:
        user = user_model.objects.create_user(
            email=user_email,
            first_name=token.get('userinfo', {}).get('given_name'),
            last_name=token.get('userinfo', {}).get('family_name')
        )

        user = update_account_to_verified(user)
    jwt = RefreshToken.for_user(user)
    access_token = str(getattr(jwt, 'access_token', ''))
    refresh_token = str(jwt)

    return redirect(settings.APP_CLIENT_URL + '/callback?t=' + access_token + '&rt=' + refresh_token)
