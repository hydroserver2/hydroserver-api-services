from django.db import models
from simple_history.models import HistoricalRecords


class HistoricalLocation(models.Model):
    thing = models.ForeignKey('Thing', on_delete=models.CASCADE, db_column='thingId')
    time = models.DateTimeField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE, db_column='locationId')
    history = HistoricalRecords(custom_model_name='HistoricalLocationChangeLog', related_name='log')

    class Meta:
        db_table = 'HistoricalLocation'
