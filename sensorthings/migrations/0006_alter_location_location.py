# Generated by Django 4.1.5 on 2023-01-24 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensorthings', '0005_rename_data_stream_observation_datastream_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='location',
            field=models.JSONField(),
        ),
    ]
