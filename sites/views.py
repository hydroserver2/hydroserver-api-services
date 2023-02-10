import json
from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from accounts.models import CustomUser, Organization
from hydroserver.settings import GOOGLE_MAPS_API_KEY
from .models import Thing, Observation, Location, Sensor, ObservedProperty, Datastream
from .forms import ThingForm, SensorForm

from .models import ThingAssociation, SensorManufacturer, SensorModel
from functools import wraps


def thing_ownership_required(func):
    """
    Decorator for site views that checks the user is logged in and is an owner of the related thing. Redirects if not
    """
    @login_required(login_url="login")
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        try:
            pk = kwargs.get('pk')
        except KeyError:
            datastream = Datastream.objects.get(id=kwargs.get('datastream_pk'))
            pk = datastream.thing.id

        thing = Thing.objects.get(id=pk)
        if not request.user.thing_associations.filter(thing=thing, owns_thing=True).exists():
            return redirect("sites")

        return func(*args, **kwargs)
    return wrapper


@login_required(login_url="login")
def sites(request):
    """
    Get all Things the user is associated with
    """
    thing_associations = request.user.thing_associations.all()

    return render(request, 'sites/sites.html', {
        'owned_things': [ta.thing for ta in thing_associations.filter(owns_thing=True)],
        'followed_things': [ta.thing for ta in thing_associations.filter(follows_thing=True)],
        'google_maps_api_key': GOOGLE_MAPS_API_KEY,
        'markers': collect_markers([ta.thing for ta in thing_associations])})


def site(request, pk):
    """
    View that gets all data related to the site to be rendered on page
    """
    thing = Thing.objects.get(id=pk)

    organization_id = json.loads(thing.properties).get('organization_id', None)
    try:
        thing_organization = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        thing_organization = "-"

    table_data = [
        {'label': 'Site Owners', 'value':
            ', '.join([associate.person.get_full_name() for associate in thing.associates.filter(owns_thing=True)])},
        {'label': 'Organization', 'value': thing_organization},
        {'label': 'Registration Date', 'value': json.loads(thing.properties).get('registration_date', None)},
        {'label': 'Deployment Date', 'value': ''},
        {'label': 'Latitude', 'value': thing.location.latitude},
        {'label': 'Longitude', 'value': thing.location.longitude},
        {'label': 'Elevation (m)', 'value': thing.location.elevation},
        {'label': 'Site Type', 'value': ''},
        {'label': 'Major Watershed', 'value': ''},
        {'label': 'Sub Basin', 'value': ''},
        {'label': 'Closest Town', 'value': thing.location.city},
        {'label': 'Notes', 'value': ''},
        {'label': 'Registration Token', 'value': ''},
        {'label': 'Sampling Feature UUID', 'value': ''},
    ]

    is_auth = request.user.is_authenticated

    return render(request, 'sites/single-site.html', {
        'thing': thing,
        'table_data': table_data,
        'owns_thing': is_auth and request.user.thing_associations.filter(thing=thing, owns_thing=True).exists(),
        'follows_thing': is_auth and request.user.thing_associations.filter(thing=thing, follows_thing=True).exists(),
        'google_maps_api_key': GOOGLE_MAPS_API_KEY,
        'markers': collect_markers([thing]),
        'is_authenticated': is_auth
    })


def register_location(new_thing, form):
    """
    View that takes a Thing and associated form data and registers it at a geographic location
    """
    new_thing.location = Location.objects.create(name='Location for ' + new_thing.name,
                                                 description=new_thing.description,
                                                 encoding_type="application/geo+json",
                                                 latitude=float(form.cleaned_data['latitude']),
                                                 longitude=float(form.cleaned_data['longitude']),
                                                 elevation=float(form.cleaned_data['elevation']),
                                                 city=form.cleaned_data['city'],
                                                 state=form.cleaned_data['state'],
                                                 country=form.cleaned_data['country'],
                                                 thing=new_thing)


@login_required(login_url="login")
def register_site(request):
    """
    registers a new site to be associated with the active user and selected organization
    """
    form = ThingForm()

    if request.method == 'POST':
        form = ThingForm(request.POST, request.FILES)
        if form.is_valid():
            new_thing = form.save()
            register_location(new_thing, form)
            properties = {"registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          "organization_id": form.cleaned_data['organizations'].pk}
            new_thing.properties = json.dumps(properties)
            new_thing.save()
            ThingAssociation.objects.create(thing=new_thing, person=request.user, owns_thing=True)
            return redirect('sites')

    context = {'form': form, 'google_maps_api_key': GOOGLE_MAPS_API_KEY}
    return render(request, "sites/site-registration.html", context)


@thing_ownership_required
def update_site(request, pk):
    thing = Thing.objects.get(id=pk)
    if request.method == 'POST':
        form = ThingForm(request.POST, instance=thing)
        if form.is_valid():
            properties = json.loads(thing.properties) if thing.properties and thing.properties != 'None' else {}
            properties["organization_id"] = form.cleaned_data['organizations'].pk
            thing.properties = json.dumps(properties)
            form.save()
            return redirect('site', pk=str(thing.id))
    else:
        form = ThingForm(instance=thing)
    return render(request, 'sites/manage_site.html', {'form': form, 'thing': thing})


@thing_ownership_required
def delete_site(request, pk):
    thing = Thing.objects.get(id=pk)
    if request.method == 'POST':
        thing.delete()
        return redirect('sites')
    context = {'object': thing}
    return render(request, 'sites/delete_template.html', context)


def update_follow(request, pk):
    """
    View which toggles if the user is following the Site
    """
    thing = Thing.objects.get(id=pk)
    follow = request.POST.get('follow')
    if follow:
        thing_association = ThingAssociation(thing=thing, person=request.user, follows_thing=True)
        thing_association.save()
    else:
        thing_association = ThingAssociation.objects.filter(thing=thing, person=request.user.id)
        thing_association.delete()
    return redirect('site', pk=str(thing.id))


@thing_ownership_required
def add_owner(request, pk):
    """
    View which allows the user to elevate another user's permissions to 'owner' for the selected Thing
    """
    thing = Thing.objects.get(id=pk)
    if request.method == 'POST':
        try:
            username = request.POST['username']
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.info(request, f'User does not exist in the system.')
            return redirect('site', pk=pk)

        thing_association, _ = ThingAssociation.objects.get_or_create(thing=thing, person=user)
        thing_association.owns_thing = True
        thing_association.follows_thing = False
        thing_association.save()
        return redirect('site', pk=pk)
    return render(request, 'sites/add-site-owner.html', {'pk': pk})


def collect_markers(things):
    """
    View which creates a list of Google Maps makers info from a collection of Things
    """
    return [
        {
            'name': thing.name,
            'description': thing.description,
            'latitude': thing.location.latitude,
            'longitude': thing.location.longitude,
            'elevation': thing.location.elevation,
            'city': thing.location.city,
            'state': thing.location.state,
            'country': thing.location.country,
            'site_url': reverse('site', args=[thing.id]),
        }
        for thing in things
    ]


def browse_sites(request):
    """
    View which collects the data for all the Things in the database to be displayed on the browse page
    """
    things = Thing.objects.all()
    return render(request, 'sites/browse-sites.html', {
        'things': things,
        'google_maps_api_key': GOOGLE_MAPS_API_KEY,
        'markers': collect_markers(things)
    })


@thing_ownership_required
def sensors(request, pk):
    """
    View which collects the sensor and datastreams for the selected Thing
    """
    thing = Thing.objects.prefetch_related('datastreams__sensor').get(id=pk)
    datastreams = [datastream for datastream in thing.datastreams.all()]
    sensors = [datastream.sensor for datastream in thing.datastreams.all()]
    return render(request, 'sites/manage-sensors.html', {
        'thing': thing,
        'sensors': sensors,
        'datastreams': datastreams
    })


@thing_ownership_required
def register_datastream(request, pk):
    """
    View which creates a new datastream for the selected Thing
    """
    thing = Thing.objects.get(pk=pk)
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
            return redirect('sensors', pk)
    else:
        form = SensorForm()
    return render(request, 'sites/register-sensor.html', {'form': form, 'thing': thing})


@thing_ownership_required
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


@thing_ownership_required
def remove_datastream(request, datastream_pk):
    datastream = Datastream.objects.get(id=datastream_pk)
    thing_pk = datastream.thing.id
    datastream.delete()
    observations = Observation.objects.filter(datastream=datastream)
    observations.delete()

    return redirect('sensors', thing_pk=thing_pk)


def get_sensor_models(request):
    """
    View which gets the list of hardware models associated with the selected manufacturer
    """
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
