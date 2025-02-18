from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings


@csrf_exempt
def index(request):

    context = {
        "proxy_base_url": settings.PROXY_BASE_URL
    }

    return render(request, "index.html", context)


@staff_member_required
def load_test_data(request):
    if request.method == "POST":
        if settings.DEBUG is False:
            messages.warning(request, "Test data is only available on development deployments.")
        else:
            try:
                call_command("load_iam_test_data")
                call_command("load_sta_test_data")
                messages.success(request, "Test data loaded successfully.")
            except Exception as e:
                messages.error(request, f"Error loading test data: {e}")
    return redirect('admin:index')


@staff_member_required
def load_default_data(request):
    if request.method == "POST":
        try:
            # call_command("load_default_data")
            messages.success(request, "Default data loaded successfully.")
        except Exception as e:
            messages.error(request, f"Error loading default data: {e}")
    return redirect('admin:index')
