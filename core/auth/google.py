from ninja import Router
from core.auth.oauth import oauth


router = Router(tags=['Google'])


@router.get('/login')
def google_login(request):
    redirect_uri = request.build_absolute_uri('/auth/google/auth')

    if 'X-Forwarded-Proto' in request.headers:
        redirect_uri = redirect_uri.replace('http:', request.headers['X-Forwarded-Proto'] + ':')

    return oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth')
def google_auth(request):

    token = oauth.google.authorize_access_token(request)
    # request.session['user'] = token['userinfo']

    return token
