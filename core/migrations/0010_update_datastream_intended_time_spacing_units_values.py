from django.db import migrations


def convert_time_spacing_uuid_to_string(apps, schema_editor):
    units = apps.get_model('core', 'Unit')
    time_spacing_units = units.objects.filter(name__in=[
        'Second', 'Minute', 'Hour', 'Day'
    ]).all()
    datastreams = apps.get_model('core', 'Datastream')
    for datastream in datastreams.objects.all():
        if datastream.intended_time_spacing_units is not None:
            try:
                time_spacing_unit_string = next((
                    time_spacing_unit.name.lower() + 's' for time_spacing_unit in time_spacing_units
                    if str(time_spacing_unit.id) == datastream.intended_time_spacing_units
                ))
            except StopIteration as e:
                raise Exception(
                    'One or more intended_time_spacing_units is using a unit other than "Second", "Minute", '
                    '"Hour", or "Day". To continue, please ensure all intended time spacing units in the '
                    'datastream table are set to one of those units and perform any necessary unit conversions on the '
                    'intended_time_spacing field, then rerun the migration.'
                ) from e
            datastream.intended_time_spacing_units = time_spacing_unit_string
            datastream.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_datastream_intended_time_spacing_units_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_time_spacing_uuid_to_string),
    ]
