from django.db import migrations, connection
from core.models import Thing, Archive


def populate_archive_link(apps, schema_editor):
    for thing in Thing.objects.all():
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT \"hydroshareArchiveResourceId\" FROM \"Thing\" WHERE id = '{str(thing.id)}'")
            row = cursor.fetchone()
            if row is not None:
                hydroshare_archive_resource_id = str(row[0])
                if hydroshare_archive_resource_id:
                    link = f"https://www.hydroshare.org/resource/{hydroshare_archive_resource_id}/"
                    Archive.objects.create(thing=thing, link=link, path='/', frequency=None)


def reverse_populate_archive_link(apps, schema_editor):
    for archive in Archive.objects.all():
        thing = archive.thing
        thing.hydroshare_archive_resource_id = archive.link.split('/')[-2]
        thing.save()
    Archive.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_archive'),
    ]

    operations = [
        migrations.RunPython(populate_archive_link, reverse_code=reverse_populate_archive_link),
    ]
