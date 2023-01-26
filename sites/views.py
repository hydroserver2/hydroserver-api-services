import json
from collections import defaultdict

from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from sensorthings.models import Thing, Observation, Location, Sensor, ObservedProperty, Datastream
from .forms import ThingForm, SensorForm

from .models import ThingOwnership, SensorManufacturer, SensorModel


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
    location = Location.objects.filter(things=thing).first().location
    try:
        location = json.loads(location)['geometry']['coordinates']
    except:
        location = [None, None]
    thing_ownership = False
    if request.user.is_authenticated:
        thing_ownership = thing_ownerships.filter(thing_id=thing, person_id=request.user).first()

    return render(request, 'sites/single-site.html', {
        'thing': thing,
        'latitude': location[0],
        'longitude': location[1],
        'thing_ownership': thing_ownership,
        'thing_owner': thing_ownerships.filter(thing_id=thing, owns_thing=True).first().person_id,
        'is_authenticated': request.user.is_authenticated
    })


def register_location(new_thing, form):
    location_data = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(form.cleaned_data['longitude']), float(form.cleaned_data['latitude'])]
        }
    }
    location_data = json.dumps(location_data)
    new_location = Location.objects.create(name='Location for ' + new_thing.name,
                                           description=new_thing.description,
                                           encoding_type="application/geo+json",
                                           location=location_data)
    new_location.things.add(new_thing)


@login_required(login_url="login")
def register_site(request):
    form = ThingForm()

    if request.method == 'POST':
        form = ThingForm(request.POST, request.FILES)
        if form.is_valid():
            new_thing = form.save()
            register_location(new_thing, form)
            ThingOwnership.objects.create(thing_id=new_thing, person_id=request.user, owns_thing=True)
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
    return render(request, 'sites/browse-sites.html', context)


def sensors(request, thing_pk):
    thing = Thing.objects.prefetch_related('datastreams__sensor').get(id=thing_pk)
    datastreams = [datastream for datastream in thing.datastreams.all()]
    sensors = [datastream.sensor for datastream in thing.datastreams.all()]
    return render(request, 'sites/manage-sensors.html', {'thing': thing, 'sensors': sensors, 'datastreams': datastreams})


def register_datastream(request, thing_pk):
    thing = Thing.objects.get(pk=thing_pk)
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # This needs to go somewhere in the model: data['sampled_medium']
            observed_property = ObservedProperty.objects.get(name=data['observed_property'])
            sensor = Sensor.objects.get(name=data['sensor_manufacturer'].name + ":" + data['sensor_model'].name)
            datastream, _ = Datastream.objects.get_or_create(name='datastream for ' + thing.name + '.' + sensor.name,
                                                             description='datastream for ' + thing.name,
                                                             unit_of_measurement=data['unit_of_measurement'],
                                                             observation_type='temp observation type',
                                                             thing=thing,
                                                             sensor=sensor,
                                                             observed_property=observed_property)
            return redirect('sensors', thing_pk)
    else:
        form = SensorForm()
    return render(request, 'sites/register-sensor.html', {'form': form, 'thing': thing})


def update_datastream(request, datastream_pk):
    datastream = Datastream.objects.get(id=datastream_pk)
    if request.method == 'POST':
        form = SensorForm(request.POST, datastream=datastream)
        if form.is_valid():
            # Get the related sensor, sensor_manufacturer, sensor_model and observed_property
            sensor_manufacturer = SensorManufacturer.objects.get(name=form.cleaned_data['sensor_manufacturer'])
            sensor_model = SensorModel.objects.get(name=form.cleaned_data['sensor_model'])
            sensor = Sensor.objects.get(name=sensor_manufacturer.name + ':' + sensor_model.name)
            observed_property = ObservedProperty.objects.get(name=form.cleaned_data['observed_property'])
            # Update the fields
            datastream.unit_of_measurement = form.cleaned_data['unit_of_measurement']
            datastream.observed_property = observed_property
            datastream.sensor = sensor
            datastream.save()
            return redirect('sensors', thing_pk=datastream.thing.id)
    else:
        form = SensorForm(datastream=datastream)
    return render(request, 'sites/update-sensor.html', {'form': form})


def remove_datastream(request, datastream_pk):
    datastream = Datastream.objects.get(id=datastream_pk)
    thing_pk = datastream.thing.id
    datastream.delete()
    observations = Observation.objects.filter(datastream=datastream)
    observations.delete()

    return redirect('sensors', thing_pk=thing_pk)


def get_sensor_models(request):
    manufacturer = request.GET.get('manufacturer')
    if manufacturer:
        sensor_models = list(SensorModel.objects.filter(manufacturer=manufacturer).values_list('name', flat=True))
        return JsonResponse(sensor_models, safe=False)
    else:
        return JsonResponse([], safe=False)


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

    observations = Observation.objects.filter(datastream__thing_id=thing_pk).select_related(
        'datastream__observed_property')

    def csv_iter():
        observed_property_names = list(
            observations.values_list('datastream__observed_property__name', flat=True).distinct())
        yield f'DateTime,{",".join(observed_property_names)}\n'

        # Group observations by result_time and yield row by row
        observations_by_time = defaultdict(lambda: {name: '' for name in observed_property_names})
        for obs in observations:
            observations_by_time[obs.result_time][obs.datastream.observed_property.name] = obs.result

        for result_time, props in observations_by_time.items():
            yield f'{result_time.strftime("%m/%d/%Y %I:%M:%S %p")},' + ','.join(props.values()) + '\n'

    response.streaming_content = csv_iter()
    return response
