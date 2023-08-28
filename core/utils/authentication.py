from functools import wraps
from django.contrib.auth import authenticate

from django.http import JsonResponse
from ninja.security import HttpBasicAuth
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from ninja.errors import HttpError

from accounts.models import CustomUser
from core.models import Datastream, ThingAssociation, Thing


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            request.authenticated_user = user
            return user


def jwt_auth(request):
    try:
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        request.authenticated_user = user
        return True
    except (KeyError, IndexError, InvalidToken, TokenError) as e:
        if isinstance(e, TokenError) and str(e) == 'Token is invalid or expired':
            raise HttpError(401, 'Token is invalid or expired')
        raise HttpError(401, 'Unauthorized')


def jwt_check_user(request):
    """
    Checks if user is logged in. Used for public views where the functionality is different for authenticated users
    """
    try:
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        untyped_token = UntypedToken(token)
        user_id = untyped_token.payload['user_id']
        user = CustomUser.objects.get(pk=user_id)
        request.user_if_there_is_one = user
    except (KeyError, IndexError, InvalidToken, TokenError) as e:
        if isinstance(e, TokenError) and str(e) == 'Token is invalid or expired':
            raise HttpError(401, 'Token is invalid or expired')
        else:
            request.user_if_there_is_one = None
    return True


def thing_ownership_required(func):
    """
    Decorator for thing views that checks the user is logged in and is an owner of the related thing.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        jwt_auth(request)

        thing_id = kwargs.get('thing_id')
        try:
            thing = Thing.objects.get(id=thing_id)
        except Thing.DoesNotExist:
            raise HttpError(403, 'Site cannot be found')
        try:
            thing_association = request.authenticated_user.thing_associations.get(thing=thing, owns_thing=True)
        except ThingAssociation.DoesNotExist:
            raise HttpError(403, 'You do not have permission to access this site.')
        request.thing_association = thing_association
        request.thing = thing
        return func(request, *args, **kwargs)

    return wrapper


def datastream_ownership_required(func):
    """
    Decorator for datastream views that checks the user is logged in and is an owner of the related datastream's thing.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        jwt_auth(request)

        datastream_id = kwargs.get('datastream_id')
        try:
            datastream = Datastream.objects.get(id=datastream_id)
        except Datastream.DoesNotExist:
            return JsonResponse({'detail': 'Datastream not found.'}, status=404)
        request.datastream = datastream
        thing = datastream.thing

        try:
            thing_association = request.authenticated_user.thing_associations.get(thing=thing, owns_thing=True)
        except ThingAssociation.DoesNotExist:
            raise HttpError(403, 'You do not have permission to access this datastream.')
        request.thing_association = thing_association

        return func(request, *args, **kwargs)

    return wrapper
