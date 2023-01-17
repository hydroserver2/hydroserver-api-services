from django.shortcuts import render, redirect

from .forms import SiteForm
from .models import Site


def sites(request):
    sites = Site.objects.all()
    context = {'sites': sites}
    return render(request, 'sites/sites.html', context)


def site(request, pk):
    site = Site.objects.get(id=pk)
    return render(request, 'sites/single-site.html', {'site': site})


# @login_required(login_url="login")
def register_site(request):
    form = SiteForm()

    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sites')

    context = {'form': form}
    return render(request, "sites/site-registration.html", context)


def delete_site(request, pk):
    site = Site.objects.get(id=pk)
    if request.method == 'POST':
        site.delete()
        return redirect('sites')
    context = {'object': site}
    return render(request, 'sites/delete_template.html', context)
