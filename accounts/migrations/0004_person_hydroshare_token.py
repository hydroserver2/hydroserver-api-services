# Generated by Django 4.2.4 on 2023-12-01 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_person_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='hydroshare_token',
            field=models.JSONField(blank=True, null=True),
        ),
    ]