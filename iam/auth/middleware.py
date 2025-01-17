from django.http import HttpResponseForbidden
from django.conf import settings


class DisableSignupMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if settings.ACCOUNT_SIGNUP_ENABLED is False:
            return None

        if request.resolver_match and request.resolver_match.url_name == 'account_signup':
            return HttpResponseForbidden("Signup is disabled.")

        if request.resolver_match and request.resolver_match.url_name == 'socialaccount_login':
            pass
