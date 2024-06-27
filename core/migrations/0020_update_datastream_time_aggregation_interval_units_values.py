from django.db import migrations
import uuid

def convert_time_aggregation_uuid_to_string(apps, schema_editor):
    units = apps.get_model('core', 'Unit')
    time_aggregation_units = units.objects.filter(name__in=[
        'Second', 'Minute', 'Hour', 'Day'
    ]).all()
    datastreams = apps.get_model('core', 'Datastream')
    for datastream in datastreams.objects.all():
        if datastream.time_aggregation_interval_units is not None:
            # To handle the case where the time_aggregation_interval_units are already converted to strings,
            # continue if the time_aggregation_interval_units isn't a UUID
            try:
                uuid.UUID(datastream.time_aggregation_interval_units)
            except ValueError:
                continue
            
            try:
                time_aggregation_unit_string = next((
                    time_aggregation_unit.name.lower() + 's' for time_aggregation_unit in time_aggregation_units
                    if str(time_aggregation_unit.id) == datastream.time_aggregation_interval_units
                ))
            except StopIteration as e:
                raise Exception(
                    'One or more time_aggregation_interval_units is using a unit other than "Second", "Minute", '
                    '"Hour", or "Day". To continue, please ensure all intended time spacing units in the '
                    'datastream table are set to one of those units and perform any necessary unit conversions on the '
                    'intended_time_aggregation field, then rerun the migration.'
                ) from e
            datastream.time_aggregation_interval_units = time_aggregation_unit_string
            datastream.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_datastream_time_aggregation_interval_units_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_time_aggregation_uuid_to_string),
    ]
