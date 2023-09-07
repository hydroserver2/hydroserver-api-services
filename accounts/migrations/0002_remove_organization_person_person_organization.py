# Generated by Django 4.1 on 2023-09-06 21:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='person',
        ),
        migrations.AddField(
            model_name='person',
            name='organization',
            field=models.OneToOneField(blank=True, db_column='organizationId', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person', to='accounts.organization'),
        ),
    ]