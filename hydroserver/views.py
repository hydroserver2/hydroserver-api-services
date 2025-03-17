from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def index(request):

    context = {
        "proxy_base_url": settings.PROXY_BASE_URL
    }

    return render(request, "index.html", context)
