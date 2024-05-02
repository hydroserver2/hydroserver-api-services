import uuid
from django.db import models
from simple_history.models import HistoricalRecords


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255, db_column='encodingType')
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    elevation_m = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    elevation_datum = models.CharField(max_length=255, null=True, blank=True, db_column='elevationDatum')
    state = models.CharField(max_length=200, null=True, blank=True)
    county = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    history = HistoricalRecords(custom_model_name='LocationChangeLog', related_name='log')

    class Meta:
        db_table = 'Location'
