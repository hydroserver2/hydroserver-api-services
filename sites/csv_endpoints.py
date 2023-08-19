import os
from collections import defaultdict

import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404

from hydroserver.settings import LOCAL_CSV_STORAGE
from .models import Thing, Observation, Sensor


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


# @thing_ownership_required
# def upload_csv(request, pk):
#     thing = get_object_or_404(Thing, pk=pk)
#     sensors = Sensor.objects.filter(datastreams__thing=thing).distinct()
#
#     if not sensors:
#         return render(request, 'sites/upload_csv.html', {'thing': thing})
#
#     if request.method == 'POST' and request.FILES.get('csv_file'):
#         sensor_form = SensorSelectionForm(request.POST, sensors=sensors)
#
#         if sensor_form.is_valid():
#             csv_file = request.FILES['csv_file']
#             fs = FileSystemStorage(location=LOCAL_CSV_STORAGE)
#             filename = fs.save(csv_file.name, csv_file)
#             file_path = os.path.join(LOCAL_CSV_STORAGE, filename)
#             process_csv_file(file_path, sensors.get(pk=sensor_form.cleaned_data['sensor']))
#
#             return render(request, 'sites/upload_csv.html', {'success': True})
#     else:
#         sensor_form = SensorSelectionForm(sensors=sensors)
#
#     return render(request, 'sites/upload_csv.html', {
#         'thing': thing,
#         'form': sensor_form,
#         'has_sensors': True
#     })


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
