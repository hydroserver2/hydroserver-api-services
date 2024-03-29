from ninja import Router
from ninja_jwt.tokens import RefreshToken
from hydroserver import settings
from django.shortcuts import redirect
from accounts.endpoints.oauth.client import oauth, user_model

oauth.register(
    name='orcid',
    server_metadata_url=settings.AUTHLIB_OAUTH_CLIENTS['orcid']['server_metadata_url'],
    client_kwargs={'scope': 'openid email profile'}
)

orcid_router = Router(tags=['ORCID OAuth 2.0'])


@orcid_router.get('/login')
def orcid_login(request):
    if settings.DEPLOYED is True:
        redirect_uri = f'{settings.PROXY_BASE_URL}/api/account/orcid/auth'
    else:
        redirect_uri = request.build_absolute_uri('/api/account/orcid/auth')

    # TODO: There's an issue with AWS that's causing the X-Forwarded-Proto header to always be set to http.
    # if 'X-Forwarded-Proto' in request.headers:
    #     redirect_uri = redirect_uri.replace('https:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.orcid.authorize_redirect(request, redirect_uri)


@orcid_router.get('/auth')
def orcid_auth(request):
    token = oauth.orcid.authorize_access_token(request)
    user_id = token.get('userinfo', {}).get('sub')
    create = False

    try:
        user = user_model.objects.get(orcid=user_id)

    except user_model.DoesNotExist:
        user = user_model.objects.create_user(
            orcid=user_id,
            first_name=token.get('userinfo', {}).get('given_name'),
            last_name=token.get('userinfo', {}).get('family_name'),
            type='other',
        )
        create = True

    jwt = RefreshToken.for_user(user)
    access_token = str(getattr(jwt, 'access_token', ''))
    refresh_token = str(jwt)

    if create:
        return redirect(f"{settings.APP_CLIENT_URL}/complete-profile?t={access_token}&rt={refresh_token}")

    return redirect(f"{settings.APP_CLIENT_URL}/login?t={access_token}&rt={refresh_token}")

