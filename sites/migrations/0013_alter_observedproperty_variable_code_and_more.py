# Generated by Django 4.1 on 2023-08-14 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0012_alter_unit_name_alter_unit_symbol_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observedproperty',
            name='variable_code',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='observedproperty',
            name='variable_type',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]