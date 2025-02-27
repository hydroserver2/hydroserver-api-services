from allauth.socialaccount.models import SocialApp
from django.views.decorators.csrf import ensure_csrf_cookie
from django.templatetags.static import static
from django.http import JsonResponse
from django.conf import settings
from iam.schemas.authentication import AuthenticationMethodsGetResponse


@ensure_csrf_cookie
def get_auth_methods(request):
    """
    Get available authentication methods.
    """

    return JsonResponse(AuthenticationMethodsGetResponse(**{
        "hydroserver_signup_enabled": settings.ACCOUNT_SIGNUP_ENABLED,
        "providers": [
            {
                "id": social_app.provider,
                "name": social_app.name,
                "icon_link": f"{settings.PROXY_BASE_URL if settings.DEPLOYMENT_BACKEND == 'local' else ''}"
                             f"{static(f'providers/{social_app.provider}.png')}",
                "signup_enabled": True if social_app.settings.get("allowSignUp") is not False else False,
                "connect_enabled": True if social_app.settings.get("allowConnection") is True else False,
            } for social_app in SocialApp.objects.all()
        ]
    }).dict(by_alias=True))
