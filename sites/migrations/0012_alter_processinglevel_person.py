# Generated by Django 4.1.5 on 2023-03-01 22:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0011_remove_featureofinterest_properties_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processinglevel',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processing_levels', to=settings.AUTH_USER_MODEL),
        ),
    ]
