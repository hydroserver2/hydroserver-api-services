from ninja import Router
from core.auth.oauth import oauth


router = Router(tags=['ORCID'])


@router.get('/login')
def orcid_login(request, close_window: bool = False):
    redirect_uri = request.build_absolute_uri('/auth/orcid/auth')

    if 'X-Forwarded-Proto' in request.headers:
        redirect_uri = redirect_uri.replace('http:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.orcid.authorize_redirect(request, redirect_uri)


@router.get('/auth')
def orcid_auth(request, close_window: bool = False):
    token = oauth.orcid.authorize_access_token(request)

    print(token)
