# Generated by Django 4.2.3 on 2023-07-31 23:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0009_alter_datastream_intended_time_spacing_units_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processinglevel',
            name='id',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='id',
        ),
    ]