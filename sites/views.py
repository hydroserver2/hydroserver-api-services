import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from sensorthings.models import Thing
from .forms import ThingForm

from .models import ThingOwnership


@login_required(login_url="login")
def sites(request):
    # Get all Things owned by the current user
    thing_ownerships = ThingOwnership.objects.filter(person_id=request.user.id)
    owned_things = [to.thing_id for to in thing_ownerships if to.owns_thing]
    followed_things = [to.thing_id for to in thing_ownerships if to.follows_thing]

    context = {'owned_things': owned_things, 'followed_things': followed_things}
    return render(request, 'sites/sites.html', context)


def site(request, pk):
    thing = Thing.objects.get(id=pk)
    # Multiple users can follow the same site, therefore:
    # Get all the ThingOwnerships related to this thing
    thing_ownerships = ThingOwnership.objects.filter(thing_id=thing)
    thing_ownership = False
    if request.user.is_authenticated:
        thing_ownership = thing_ownerships.filter(thing_id=thing, person_id=request.user).first()

    return render(request, 'sites/single-site.html', {
        'thing': thing,
        'thing_ownership': thing_ownership,
        'is_authenticated': request.user.is_authenticated
    })


@login_required(login_url="login")
def register_site(request):
    form = ThingForm()

    if request.method == 'POST':
        form = ThingForm(request.POST, request.FILES)
        if form.is_valid():
            new_thing = form.save()
            thing_ownership = ThingOwnership(thing_id=new_thing, person_id=request.user, owns_thing=True)
            thing_ownership.save()
            return redirect('sites')

    context = {'form': form}
    return render(request, "sites/site-registration.html", context)


def delete_site(request, pk):
    thing = Thing.objects.get(id=pk)
    if request.method == 'POST':
        thing.delete()
        return redirect('sites')
    context = {'object': thing}
    return render(request, 'sites/delete_template.html', context)


def update_follow(request, pk):
    thing = Thing.objects.get(id=pk)
    follow = request.POST.get('follow')
    if follow:
        thing_ownership = ThingOwnership(thing_id=thing, person_id=request.user, follows_thing=True)
        thing_ownership.save()
    else:
        thing_ownership = ThingOwnership.objects.filter(thing_id=thing, person_id=request.user.id)
        thing_ownership.delete()
    return redirect('site', pk=str(thing.id))


def browse_sites(request):
    things = Thing.objects.all()
    context = {'things': things}
    return render(request,  'sites/browse-sites.html', context)
