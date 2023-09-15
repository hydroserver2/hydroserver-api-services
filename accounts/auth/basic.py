from ninja.security import HttpBasicAuth
from django.contrib.auth import authenticate


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password, *args, **kwargs):
        user = authenticate(email=username, password=password)
        if user and user.is_authenticated:
            request.authenticated_user = user
            return user
