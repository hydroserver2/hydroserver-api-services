import json

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from ninja import Schema, NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import RefreshToken
from ninja.errors import HttpError

from accounts.models import CustomUser

api = NinjaAPI()


@api.post('/token')
def get_token(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    user = authenticate(username=email, password=password)
    if user:
        token = RefreshToken.for_user(user)
        return {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
        }
    else:
        return HttpError(401, 'Invalid credentials')


@api.get("/hello")
def hello(request):
    return "Hello world"


class CreateUserInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None


@api.post('/users/')
def create_user(request, data: CreateUserInput):
    try:
        user = CustomUser.objects.create_user(
            username=data.email,
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    except Exception as e:
        raise HttpError(400, str(e))
    user.middle_name = data.middle_name
    user.phone = data.phone
    user.address = data.address
    user.save()
    return {'id': user.id, 'username': user.username}


# @router.get('/users/{user_id}', auth=HttpBearer())
# def get_user(request, user_id: int):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         return {
#             'id': user.id,
#             'username': user.username,
#         }
#     except CustomUser.DoesNotExist:
#         return HttpError(404, 'User not found')
