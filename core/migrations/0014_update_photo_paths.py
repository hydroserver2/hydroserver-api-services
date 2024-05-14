# Generated by Django 4.2 on 2024-04-24 19:39

from urllib.parse import urlparse
from django.db import migrations, models


def update_file_path(apps, schema_editor):
    photo_model = apps.get_model('core', 'Photo')
    for photo in photo_model.objects.all():
        photo.file_path = urlparse(photo.link).path[1:]
        photo.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_merge_20240320_2159'),
    ]

    operations = [
        migrations.RunPython(update_file_path),
    ]