import os
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def index(request):
    vue_index_path = os.path.join(settings.BASE_DIR, "web", "index.html")
    context = {"proxy_base_url": settings.PROXY_BASE_URL}

    if os.path.exists(vue_index_path) and settings.STORAGES.get("web"):
        return FileResponse(open(vue_index_path, "rb"), content_type="text/html")
    else:
        return render(request, "index.html", context)


def spa_router(request, path=""):
    if os.path.splitext(path)[1]:
        raise Http404()

    try:
        vue_index_path = os.path.join(settings.BASE_DIR, "web", "index.html")
        return FileResponse(open(vue_index_path, "rb"), content_type="text/html")
    except FileNotFoundError:
        raise Http404()
