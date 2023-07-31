# Generated by Django 4.2.3 on 2023-07-31 23:12

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0006_alter_datastream_processing_level_uuid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datastream',
            name='time_aggregation_interval_units',
        ),
        migrations.AlterField(
            model_name='datastream',
            name='intended_time_spacing_units_uuid',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='intended_time_spacing_uuid', to='sites.unit'),
        ),
        migrations.AlterField(
            model_name='datastream',
            name='time_aggregation_interval_units_uuid',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='time_aggregation_interval_uuid', to='sites.unit'),
        ),
        migrations.AlterField(
            model_name='datastream',
            name='unit_uuid',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unit_uuid', to='sites.unit'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='unit',
            name='new_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]