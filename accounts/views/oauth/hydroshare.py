from ninja import Router
from urllib.parse import urlsplit, parse_qs
from hydroserver import settings
from django.shortcuts import redirect
from accounts.views.oauth.client import oauth
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from accounts.models import Person


oauth.register(
    name='hydroshare'
)

hydroshare_router = Router(tags=['HydroShare OAuth 2.0'])


@hydroshare_router.get(
    '/connect',
    auth=[JWTAuth(), BasicAuth()],
)
def hydroshare_connect(request):
    if settings.DEPLOYED is True:
        redirect_uri = f'{settings.PROXY_BASE_URL}/api/account/hydroshare/auth'
    else:
        redirect_uri = request.build_absolute_uri('/api/account/hydroshare/auth')

    # TODO: There's an issue with AWS that's causing the X-Forwarded-Proto header to always be set to http.
    # if 'X-Forwarded-Proto' in request.headers:
    #     redirect_uri = redirect_uri.replace('https:', request.headers['X-Forwarded-Proto'] + ':')

    request.session['_hydroshare_connect_{}'] = str(getattr(request, 'authenticated_user'))

    authorized_redirect = oauth.hydroshare.authorize_redirect(request, redirect_uri)
    state = dict(parse_qs(urlsplit(authorized_redirect.url).query))['state'][0]
    request.session[f'_hydroshare_connect_{state}'] = str(getattr(request, 'authenticated_user'))

    return authorized_redirect


@hydroshare_router.get('/auth')
def hydroshare_auth(request):

    token = oauth.hydroshare.authorize_access_token(request)
    user = Person.objects.get(email=request.session[f'_hydroshare_connect_{request.GET["state"]}'])

    user.hydroshare_token = token
    user.save()

    # return redirect(settings.APP_CLIENT_URL + '/callback?t=' + access_token + '&rt=' + refresh_token)
