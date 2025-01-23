from django.shortcuts import render
from django.conf import settings


def index(request):

    context = {
        'proxy_base_url': settings.PROXY_BASE_URL
    }

    return render(request, 'index.html', context)
