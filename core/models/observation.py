import uuid
import pytz
from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models import Datastream, FeatureOfInterest


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datastream = models.ForeignKey(Datastream, on_delete=models.CASCADE, db_column='datastreamId')
    feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.PROTECT, null=True, blank=True,
                                            db_column='featureOfInterestId')
    phenomenon_time = models.DateTimeField(db_column='phenomenonTime')
    result = models.FloatField()
    result_time = models.DateTimeField(null=True, blank=True, db_column='resultTime')
    quality_code = models.CharField(max_length=255, null=True, blank=True, db_column='qualityCode')
    result_qualifiers = ArrayField(models.UUIDField(), null=True, blank=True, db_column='resultQualifiers')

    def save(self, *args, **kwargs):
        if not self.phenomenon_time:
            self.phenomenon_time = datetime.now(pytz.utc)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Observation'
        managed = False