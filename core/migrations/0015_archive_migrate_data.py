from django.db import migrations
from core.models import Thing, Archive


def populate_archive_link(apps, schema_editor):
    for thing in Thing.objects.all():
        if thing.hydroshare_archive_resource_id:
            link = f"https://www.hydroshare.org/resource/{thing.hydroshare_archive_resource_id}/"
            Archive.objects.create(thing=thing, link=link, path='/', frequency=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_archive'),
    ]

    operations = [
        migrations.RunPython(populate_archive_link),
    ]
