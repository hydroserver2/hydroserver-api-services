import uuid
from django.db import models
from simple_history.models import HistoricalRecords


class FeatureOfInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255, db_column='encodingType')
    feature = models.TextField()
    history = HistoricalRecords(custom_model_name='FeatureOfInterestChangeLog', related_name='log')

    class Meta:
        db_table = 'FeatureOfInterest'
