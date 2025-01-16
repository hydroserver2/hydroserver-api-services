from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings


def index(request):

    context = {
        'proxy_base_url': settings.PROXY_BASE_URL
    }

    return render(request, 'index.html', context)


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"details": "CSRF cookie set"})


@ensure_csrf_cookie
def supported_logins(request):


    return JsonResponse({})
