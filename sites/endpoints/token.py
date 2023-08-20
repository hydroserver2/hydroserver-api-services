from ninja import Router, Schema
from .user import user_to_dict
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from accounts.models import CustomUser

router = Router()

class GetTokenInput(Schema):
    email: str
    password: str


@router.post('')
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


class CreateRefreshInput(Schema):
    refresh_token: str


@router.post("/refresh")
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