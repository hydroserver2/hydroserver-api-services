# Generated by Django 4.2 on 2024-04-24 19:39

import django.core.files.storage.filesystem
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_update_photo_paths'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='file_path',
            field=models.FileField(db_column='filePath', storage=django.core.files.storage.filesystem.FileSystemStorage, upload_to='photos'),
        ),
        migrations.AlterField(
            model_name='photochangelog',
            name='file_path',
            field=models.TextField(db_column='filePath', max_length=100),
        ),
        migrations.RemoveField(
            model_name='photo',
            name='link',
        ),
        migrations.RemoveField(
            model_name='photochangelog',
            name='link',
        ),
    ]
