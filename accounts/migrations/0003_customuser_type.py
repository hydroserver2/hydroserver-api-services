# Generated by Django 4.1 on 2023-05-05 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]