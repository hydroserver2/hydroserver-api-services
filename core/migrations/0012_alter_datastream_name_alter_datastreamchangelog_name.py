# Generated by Django 4.2 on 2024-03-19 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_location_country_locationchangelog_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datastream',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='datastreamchangelog',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
