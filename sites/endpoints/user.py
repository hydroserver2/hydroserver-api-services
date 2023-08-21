from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken

from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import CustomUser, PasswordReset
from sites.utils.authentication import jwt_auth
from sites.utils.user import user_to_dict, send_password_reset_email
from sites.models import Thing

router = Router()

class CreateUserInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str = None
    organization: str = None
    link: str = None


@router.post('')
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
            link=data.link,
            phone=data.phone,
            address=data.address
        )
    except IntegrityError:
        raise HttpError(400, 'EmailAlreadyExists')
    except Exception as e:
        raise HttpError(400, str(e))

    user = authenticate(username=data.email, password=data.password)
    user.save()

    token = RefreshToken.for_user(user)

    return {
        'access_token': str(token.access_token),
        'refresh_token': str(token),
    }


class UpdateUserInput(Schema):
    first_name: str = None
    last_name: str = None
    middle_name: str = None
    phone: str = None
    address: str = None
    organization: str = None
    type: str = None
    link: str = None


@router.patch('', auth=jwt_auth)
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
    if data.link is not None:
        user.link = data.link

    user.save()
    return JsonResponse(user_to_dict(user))


@router.delete('', auth=jwt_auth)
@transaction.atomic
def delete_user(request):
    try:
        Thing.objects.filter(associates__person=request.authenticated_user, associates__is_primary_owner=True).delete()
        request.authenticated_user.delete()
        logout(request)
        return {'detail': 'Your account has been removed!'}
    except CustomUser.DoesNotExist:
        raise HttpError(404, 'User not found')


class ResetPasswordInput(Schema):
    uid: str
    token: str
    password: str

@router.post("/reset_password")
def reset_password(request, data: ResetPasswordInput):
    try:
        password_reset = PasswordReset.objects.get(pk=data.uid)
    except (PasswordReset.DoesNotExist):
        return JsonResponse({'error': 'Invalid UID'}, status=400)
        
    user = password_reset.user

    if not default_token_generator.check_token(user, data.token):
        return JsonResponse({'error': 'Invalid or expired token'}, status=400)

    user.set_password(data.password)
    user.save()
    password_reset.delete()

    return JsonResponse({'message': 'Password reset successful'}, status=200)


class PasswordResetRequestInput(Schema):
    email: str


@router.post("/password_reset")
def password_reset(request, data: PasswordResetRequestInput):
    try:
        user = CustomUser.objects.filter(email=data.email).first()
        if user:
            try:
                password_reset = PasswordReset(user=user)
                password_reset.save()
            except IntegrityError:
                PasswordReset.objects.get(user=user).delete()
                password_reset = PasswordReset(user=user)
                password_reset.save()

            token = default_token_generator.make_token(user)
            send_password_reset_email(user, password_reset.id, token)
            
            return JsonResponse({'message': 'Password reset email sent.'}, status=200)
        else:
            return JsonResponse({'detail': 'User does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    