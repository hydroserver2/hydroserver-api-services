# Generated by Django 4.2.4 on 2023-09-20 22:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QualifierAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'QualifierAssociation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ResultQualifier',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'ResultQualifier',
            },
        ),
    ]
