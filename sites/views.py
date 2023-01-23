from collections import defaultdict

from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from sensorthings.models import Thing, Observation
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


def export_csv(request, thing_pk):
    """
    This algorithm exports all the observations associated with the passed in thing_pk into a CSV file in O(n) time.
    The use of select_related() improves the efficiency of the algorithm by reducing the number of database queries.
    This iterates over the observations once, storing the observations in a dictionary, then yields the rows one by one.
    This algorithm is memory-efficient since it doesn't load the whole data into memory.
    """
    thing = Thing.objects.get(id=thing_pk)
    response = StreamingHttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(thing.name)

    observations = Observation.objects.filter(data_stream__thing_id=thing_pk).select_related('data_stream__observed_property')

    def csv_iter():
        observed_property_names = list(observations.values_list('data_stream__observed_property__name', flat=True).distinct())
        yield f'DateTime,{",".join(observed_property_names)}\n'

        # Group observations by result_time and yield row by row
        observations_by_time = defaultdict(lambda: {name: '' for name in observed_property_names})
        for obs in observations:
            observations_by_time[obs.result_time][obs.data_stream.observed_property.name] = obs.result

        for result_time, props in observations_by_time.items():
            yield f'{result_time.strftime("%m/%d/%Y %I:%M:%S %p")},' + ','.join(props.values()) + '\n'

    response.streaming_content = csv_iter()
    return response
