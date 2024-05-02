import base64
from ninja import Router, Query
from urllib.parse import urlsplit, parse_qs
from hydroserver import settings
from hydroserver.auth import JWTAuth, BasicAuth
from django.shortcuts import redirect
from accounts.endpoints.oauth.client import oauth
from accounts.models import Person
from accounts.endpoints.user.utils import account_verification_token


oauth.register(
    name='hydroshare'
)

hydroshare_router = Router(tags=['HydroShare OAuth 2.0'])


@hydroshare_router.get(
    '/connect',
    auth=[JWTAuth(), BasicAuth()]
)
def hydroshare_verify(request):
    uid = base64.urlsafe_b64encode(bytes(request.authenticated_user.email, 'utf-8'))
    token = account_verification_token.make_token(request.authenticated_user)

    return 200, {'uid': str(uid.decode('utf-8')), 'token': token}


@hydroshare_router.get(
    '/login'
)
def hydroshare_connect(request, uid: str = Query(...), token: str = Query(...)):

    user = Person.objects.get(email=base64.b64decode(uid).decode('utf-8'))
    if not account_verification_token.check_token(user, token):
        return 400, 'Invalid or expired token'

    if settings.DEPLOYMENT_BACKEND == 'aws':
        redirect_uri = f'{settings.PROXY_BASE_URL}/api/account/hydroshare/auth'
    else:
        redirect_uri = request.build_absolute_uri('/api/account/hydroshare/auth')

    # TODO: There's an issue with AWS that's causing the X-Forwarded-Proto header to always be set to http.
    # if 'X-Forwarded-Proto' in request.headers:
    #     redirect_uri = redirect_uri.replace('https:', request.headers['X-Forwarded-Proto'] + ':')

    authorized_redirect = oauth.hydroshare.authorize_redirect(request, redirect_uri)
    state = dict(parse_qs(urlsplit(authorized_redirect.url).query))['state'][0]
    request.session[f'_hydroshare_connect_{state}'] = str(user)

    return authorized_redirect


@hydroshare_router.get('/auth')
def hydroshare_auth(request):

    token = oauth.hydroshare.authorize_access_token(request)
    user = Person.objects.get(email=request.session[f'_hydroshare_connect_{request.GET["state"]}'])

    user.hydroshare_token = token
    user.save()

    return redirect(settings.APP_CLIENT_URL + '/profile?refresh=true')


@hydroshare_router.get(
    '/disconnect',
    auth=[JWTAuth(), BasicAuth()]
)
def hydroshare_disconnect(request):

    user = request.authenticated_user
    user.hydroshare_token = None
    user.save()

    return 200, None
