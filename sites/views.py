import os
from collections import defaultdict

import pandas as pd
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from accounts.models import CustomUser
from hydroserver.settings import GOOGLE_MAPS_API_KEY, LOCAL_CSV_STORAGE
from .models import Thing, Observation, Location, Sensor, ObservedProperty, Datastream, ThingAssociation, Unit, \
    ProcessingLevel
from .forms import ThingForm, SensorSelectionForm, DatastreamForm, MethodForm, ObservedPropertyForm, UnitForm, \
    ProcessingLevelForm

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
            if not pk:
                datastream = Datastream.objects.get(id=kwargs.get('datastream_pk'))
                pk = datastream.thing.id
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

    site_owners = thing.associates.filter(owns_thing=True)
    table_data = [
        {'label': f'Site Owner{"s" if len(site_owners) != 1 else ""}',
         'value': ', '.join([f"{owner.person.get_full_name()} ({owner.person.organization or 'No Org'})"
                             for owner in site_owners])},
        # {'label': 'Registration Date', 'value': json.loads(thing.properties).get('registration_date', None)},
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
        'datastreams': thing.datastreams.all(),
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
    registers a new site to be associated with the active user
    """
    form = ThingForm()

    if request.method == 'POST':
        form = ThingForm(request.POST, request.FILES)
        if form.is_valid():
            new_thing = form.save()
            register_location(new_thing, form)
            # properties = {"registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            # new_thing.properties = json.dumps(properties)
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


def add_sensor(request):
    form = MethodForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        Sensor.objects.create(
            person=request.user,
            name=data.get('name', None) or 'Sensor time series',
            description=data.get('description', None) or 'A time series of observations derived from a sensor',
            manufacturer=data.get('manufacturer', None),
            model=data.get('model', None),
            method_type=data.get('method_type', None),
            method_code=data.get('method_code', None),
            method_link=data.get('method_link', None)
        )


def add_datastream(request, thing):
    form = DatastreamForm(request.POST, user=request.user)
    if form.is_valid():
        data = form.cleaned_data
        sensor = Sensor.objects.get(id=data['method'])
        Datastream.objects.create(
            name=str(sensor),
            description='description',
            observed_property=ObservedProperty.objects.get(id=data['observed_property'].id),
            unit=Unit.objects.get(id=data['unit'].id),
            processing_level=data.get('processing_level', None),
            sampled_medium=data.get('sampled_medium', None),
            status=data.get('status', None),
            no_data_value=data.get('no_data_value', None),
            aggregation_statistic=data.get('aggregation_statistic', None),
            # intended_time_spacing=data.get('intended_time_spacing', None),
            # intended_time_spacing_units=Unit.objects.get(id=data['intended_time_spacing_units'].id),
            # time_aggregation_interval=data.get('time_aggregation_interval', None),
            # time_aggregation_interval_units=Unit.objects.get(id=data['time_aggregation_interval_units'].id),
            result_type='Time Series Coverage',
            observation_type='OM_Measurement',
            thing=thing,
            sensor=sensor,
        )


def add_observed_property(request):
    form = ObservedPropertyForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        ObservedProperty.objects.get_or_create(
            name=data.get('name', None),
            person=request.user,
            definition=data.get('definition', None),
            description=data.get('description', None)
        )


def add_unit(request):
    form = UnitForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        Unit.objects.get_or_create(
            name=data.get('name', None),
            person=request.user,
            definition=data.get('definition', None),
            unit_type=data.get('unit_type', None)
        )


def add_processing_level(request):
    form = ProcessingLevelForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        ProcessingLevel.objects.get_or_create(
            processing_level_code=data.get('processing_level_code', None),
            person=request.user,
            definition=data.get('definition', None),
            explanation=data.get('explanation', None)
        )


@login_required
def datastream(request, pk):
    datastream = get_object_or_404(Datastream, pk=pk)
    return render(request, 'sites/manage-datastreams.html', {
        'datastream': datastream,
        'owns_datastream': datastream.thing.associates.filter(person=request.user, owns_thing=True).exists()
    })


@thing_ownership_required
def register_datastream(request, pk):
    """
    View which creates a new datastream for the selected Thing
    """
    thing = Thing.objects.get(pk=pk)
    thing_ids = request.user.thing_associations.filter(owns_thing=True).values('thing__id')
    datastreams = Datastream.objects.filter(thing__id__in=thing_ids)
    datastream_form = DatastreamForm(user=request.user)
    if request.method == 'POST':
        if 'datastream_form' in request.POST:
            add_datastream(request, thing)
            return HttpResponseRedirect(reverse('site', args=[pk]))
        elif 'datastream_id' in request.POST:
            pass
            # This need to populate the form with the passed in datastream instance
            # datastream_id = int(request.POST['datastream_id'])
            # datastream = get_object_or_404(Datastream, pk=datastream_id)
            # datastream = get_object_or_404(Datastream, pk=int(request.POST.get('datastream_id')))
            # datastream_form = DatastreamForm(request.POST or None, instance=datastream, user=request.user)
        elif 'method_form' in request.POST:
            add_sensor(request)
        elif 'observed_property_form' in request.POST:
            add_observed_property(request)
        elif 'unit_form' in request.POST:
            add_unit(request)
        elif 'processing_level_form' in request.POST:
            add_processing_level(request)
        return HttpResponseRedirect(reverse('register_datastream', args=[pk]))

    return render(request, 'sites/register-datastream.html', {
        'datastream_form': datastream_form,
        'method_form': MethodForm(),
        'observed_property_form': ObservedPropertyForm(),
        'unit_form': UnitForm(),
        'processing_level_form': ProcessingLevelForm(),
        'thing': thing,
        'datastreams': datastreams,
    })


@thing_ownership_required
def update_datastream(request, datastream_pk):
    datastream = get_object_or_404(Datastream, pk=datastream_pk)
    form = DatastreamForm(request.POST or None, instance=datastream, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            new_datastream = form.save(commit=False)
            new_datastream.sensor = Sensor.objects.get(pk=form.cleaned_data['method'])
            new_datastream.save()
            return redirect('site', pk=datastream.thing.pk)
        else:
            print(form.errors)
    return render(request, 'sites/update_datastream.html', {'form': form})


@thing_ownership_required
def remove_datastream(request, datastream_pk):
    datastream = Datastream.objects.get(id=datastream_pk)
    thing_pk = datastream.thing.id
    datastream.delete()
    observations = Observation.objects.filter(datastream=datastream)
    observations.delete()

    return redirect('site', pk=thing_pk)


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
            observations_by_time[obs.phenomenon_time][obs.datastream.observed_property.name] = obs.result

        for result_time, props in observations_by_time.items():
            yield f'{result_time.strftime("%m/%d/%Y %I:%M:%S %p")},' + ','.join(props.values()) + '\n'

    response.streaming_content = csv_iter()
    return response


@thing_ownership_required
def upload_csv(request, pk):
    thing = get_object_or_404(Thing, pk=pk)
    sensors = Sensor.objects.filter(datastreams__thing=thing).distinct()

    if not sensors:
        return render(request, 'sites/upload_csv.html', {'thing': thing})

    if request.method == 'POST' and request.FILES.get('csv_file'):
        sensor_form = SensorSelectionForm(request.POST, sensors=sensors)

        if sensor_form.is_valid():
            csv_file = request.FILES['csv_file']
            fs = FileSystemStorage(location=LOCAL_CSV_STORAGE)
            filename = fs.save(csv_file.name, csv_file)
            file_path = os.path.join(LOCAL_CSV_STORAGE, filename)
            process_csv_file(file_path, sensors.get(pk=sensor_form.cleaned_data['sensor']))

            return render(request, 'sites/upload_csv.html', {'success': True})
    else:
        sensor_form = SensorSelectionForm(sensors=sensors)

    return render(request, 'sites/upload_csv.html', {
        'thing': thing,
        'form': sensor_form,
        'has_sensors': True
    })


def process_csv_file(file_path, sensor):
    metadata = pd.read_csv(file_path, nrows=1, header=None).values.tolist()[0]
    df = pd.read_csv(file_path, header=1,
                     usecols=[datastream.observed_property.name for datastream in sensor.datastreams.all() if
                              datastream.observed_property] + ["TIMESTAMP"])
    units = df.iloc[0]
    measurement_type = df.iloc[1]
    df = df.drop([0, 1])

    time_series = df.iloc[:, 0]

    observations = []
    for datastream in sensor.datastreams.all():
        column_name = datastream.observed_property.name
        if column_name not in df.columns:
            continue
        data = df[column_name]

        for j, time in enumerate(time_series):
            observations.append(Observation(phenomenon_time=time, result=data[j], datastream=datastream))

        Observation.objects.bulk_create(observations)
