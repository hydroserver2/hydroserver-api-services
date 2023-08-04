import json
from hydroserver.api.api import api
from django.contrib.auth import authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from ninja.errors import HttpError
from accounts.models import CustomUser
from hydroserver.api.util import jwt_auth, user_to_dict
from hydroserver.schemas import CreateRefreshInput, CreateUserInput, GetTokenInput, PasswordResetInput, UpdateUserInput
from sites.models import Thing
from ninja.security import HttpBasicAuth
from authlib.integrations.django_client import OAuth


# ===================================================
#   OAUTH 2.0
# ===================================================

# configs are loaded from entry in `AUTHLIB_OAUTH_CLIENTS`.
# https://docs.authlib.org/en/latest/client/django.html#configuration
oauth = OAuth()
oauth.register(name='orcid')


@api.get('/login')
def login(request, window_close: bool = False):
    print('Redirecting...')
    redirect_uri = request.build_absolute_uri('/api/auth')

    if 'X-Forwarded-Proto' in request.headers:
        redirect_uri = redirect_uri.replace('http:', request.headers['X-Forwarded-Proto'] + ':')

    redirect = oauth.orcid.authorize_redirect(request, redirect_uri + f"?window_close={window_close}")

    return redirect


@api.get('/logout')
def logout(request):
    #TODO: log user out by removing user data from session
    pass


@api.get('/auth')
def authorize(request, window_close: bool = False):
    print('Authorizing...')
    try:
        token = oauth.orcid.authorize_access_token(request)
        # TODO: find way to get user
        resp = oauth.orcid.get('user', token=token)
        resp.raise_for_status()
        profile = resp.json()
        print(profile)
    except (KeyError, IndexError, InvalidToken, TokenError) as e:
        pass
        # return HTMLResponse(f'<h1>{e.error}</h1>')
    
    # TODO: get user token and data using `profile` data
    user = CustomUser.objects.get(email=profile.email)
    token = RefreshToken.for_user(user)

    if user and window_close:
        responseHTML = '<html><head><title>HydroServer Sign In</title></head><body></body><script>res = %value%; window.opener.postMessage(res, "*");window.close();</script></html>'
        responseHTML = responseHTML.replace(
            "%value%", json.dumps({
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'user': user_to_dict(user)
          })
        )
        # return HTMLResponse(responseHTML)

    # return Response(token)


@api.post("/token/refresh")
def refresh_token(request, data: CreateRefreshInput):
    try:
        token = data.refresh_token
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        new_token = RefreshToken.for_user(user)
        return JsonResponse({
            'access_token': str(new_token.access_token),
            'refresh_token': str(new_token),
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=401)
    except (InvalidToken, TokenError, KeyError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=401)


# ===================================================
#   BASIC AUTHENTICATION
# ===================================================


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            request.authenticated_user = user
            return user
        

# @api.get("/user", auth=jwt_auth)
# def get_user(request):
#     return JsonResponse(user_to_dict(request.authenticated_user))


@api.post('/token')
def get_token(request, data: GetTokenInput):
    email = data.email
    password = data.password
    user = authenticate(username=email, password=password)
    if user:
        token = RefreshToken.for_user(user)
        return {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'user': user_to_dict(user)
        }
    else:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)


@api.post("/password_reset")
def password_reset(request, data: PasswordResetInput):
    data_dict = data.dict()
    form = PasswordResetForm(data_dict)
    if form.is_valid():
        opts = {
            'use_https': request.is_secure(),
            'token_generator': default_token_generator,
            'from_email': None,
            'email_template_name': 'registration/password_reset_email.html',
            'request': request,
        }
        user = CustomUser.objects.filter(email=data.email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return JsonResponse({'uid': uid, 'token': token})
        else:
            return JsonResponse({'detail': 'User does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'An error occurred.'}, status=400)
    

@api.post('/user')
def create_user(request, data: CreateUserInput):
    try:
        user = CustomUser.objects.create_user(
            username=data.email,
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
    except Exception as e:
        raise HttpError(400, str(e))

    user = authenticate(username=data.email, password=data.password)
    user.save()

    token = RefreshToken.for_user(user)

    return {
        'access_token': str(token.access_token),
        'refresh_token': str(token),
    }

@api.patch('/user', auth=jwt_auth)
def update_user(request, data: UpdateUserInput):
    user = request.authenticated_user

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.middle_name is not None:
        user.middle_name = data.middle_name
    if data.phone is not None:
        user.phone = data.phone
    if data.address is not None:
        user.address = data.address
    if data.organization is not None:
        user.organization = data.organization
    if data.type is not None:
        user.type = data.type

    user.save()
    return JsonResponse(user_to_dict(user))


@api.delete('/user', auth=jwt_auth)
@transaction.atomic
def delete_user(request):
    try:
        Thing.objects.filter(associates__person=request.authenticated_user, associates__is_primary_owner=True).delete()
        request.authenticated_user.delete()
        logout(request)
        return {'detail': 'Your account has been removed!'}
    except CustomUser.DoesNotExist:
        raise HttpError(404, 'User not found')