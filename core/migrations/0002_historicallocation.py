# Generated by Django 4.1 on 2023-08-31 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.location')),
                ('thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.thing')),
            ],
            options={
                'db_table': 'HistoricalLocation',
            },
        ),
    ]
