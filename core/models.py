import uuid
import pytz
import boto3
from datetime import datetime
from django.db import models, IntegrityError
from django.db.models import ForeignKey
from django.db.models.signals import pre_delete
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
from accounts.models import Person
from botocore.exceptions import ClientError
from hydroserver.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, PROXY_BASE_URL


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


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    sampling_feature_type = models.CharField(max_length=200, db_column='samplingFeatureType')
    sampling_feature_code = models.CharField(max_length=200, db_column='samplingFeatureCode')
    site_type = models.CharField(max_length=200, db_column='siteType')
    is_private = models.BooleanField(default=False, db_column='isPrivate')
    data_disclaimer = models.TextField(null=True, blank=True, db_column='dataDisclaimer')
    hydroshare_archive_resource_id = models.CharField(
        max_length=500, blank=True, null=True, db_column='hydroshareArchiveResourceId'
    )
    location = models.OneToOneField(Location, related_name='thing', on_delete=models.CASCADE, db_column='locationId')
    history = HistoricalRecords(custom_model_name='ThingChangeLog', related_name='log')

    class Meta:
        db_table = 'Thing'


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.ForeignKey('Thing', related_name='tags', on_delete=models.CASCADE, db_column='thingId')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'Tag'
        unique_together = ('thing', 'key', 'value')


class HistoricalLocation(models.Model):
    thing = models.ForeignKey('Thing', on_delete=models.CASCADE, db_column='thingId')
    time = models.DateTimeField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE, db_column='locationId')
    history = HistoricalRecords(custom_model_name='HistoricalLocationChangeLog', related_name='log')

    class Meta:
        db_table = 'HistoricalLocation'


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.ForeignKey('Thing', related_name='photos', on_delete=models.CASCADE, db_column='thingId')
    file_path = models.CharField(max_length=1000, db_column='filePath')
    link = models.URLField(max_length=2000)
    history = HistoricalRecords(custom_model_name='PhotoChangeLog', related_name='log')

    class Meta:
        db_table = 'Photo'


@receiver(pre_delete, sender=Photo)
def delete_photo(sender, instance, **kwargs):
    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    file_name = instance.link.split(f'{PROXY_BASE_URL}/')[1]

    try:
        s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_name)
    except ClientError as e:
        print(f'Error deleting {file_name} from S3: {e}')


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, db_column='personId')
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255, db_column='encodingType')
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    model_link = models.CharField(max_length=500, null=True, blank=True, db_column='modelLink')
    method_type = models.CharField(max_length=100, db_column='methodType')
    method_link = models.CharField(max_length=500, blank=True, null=True, db_column='methodLink')
    method_code = models.CharField(max_length=50, blank=True, null=True, db_column='methodCode')
    history = HistoricalRecords(custom_model_name='SensorChangeLog', related_name='log')

    def __str__(self):
        if self.method_type and self.method_type.strip().lower().replace(" ", "") == 'instrumentdeployment':
            return f"{self.manufacturer}:{self.model}"
        else:
            return f"{self.method_type}:{self.method_code}"

    class Meta:
        db_table = 'Sensor'


class ObservedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, db_column='personId')
    name = models.CharField(max_length=255)
    definition = models.TextField()
    description = models.TextField()
    type = models.CharField(max_length=500)
    code = models.CharField(max_length=500)
    history = HistoricalRecords(custom_model_name='ObservedPropertyChangeLog', related_name='log')

    class Meta:
        db_table = 'ObservedProperty'


class FeatureOfInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255, db_column='encodingType')
    feature = models.TextField()
    history = HistoricalRecords(custom_model_name='FeatureOfInterestChangeLog', related_name='log')

    class Meta:
        db_table = 'FeatureOfInterest'


class ProcessingLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='processing_levels', null=True,
                               blank=True, db_column='personId')
    code = models.CharField(max_length=255)
    definition = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    history = HistoricalRecords(custom_model_name='ProcessingLevelChangeLog', related_name='log')

    class Meta:
        db_table = 'ProcessingLevel'


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, db_column='personId')
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    definition = models.TextField()
    type = models.CharField(max_length=255)
    history = HistoricalRecords(custom_model_name='UnitChangeLog', related_name='log')

    class Meta:
        db_table = 'Unit'


class DataLoader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='data_loaders', db_column='personId')
    history = HistoricalRecords(custom_model_name='DataLoaderChangeLog', related_name='log')

    class Meta:
        db_table = 'DataLoader'


class DataSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    header_row = models.PositiveIntegerField(null=True, blank=True, db_column='headerRow')
    data_start_row = models.PositiveIntegerField(null=True, blank=True, db_column='dataStartRow')
    delimiter = models.CharField(max_length=1, null=True, blank=True)
    quote_char = models.CharField(max_length=1, null=True, blank=True, db_column='quoteChar')
    interval = models.PositiveIntegerField(null=True, blank=True)
    interval_units = models.CharField(max_length=255, null=True, blank=True, db_column='intervalUnits')
    crontab = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True, db_column='startTime')
    end_time = models.DateTimeField(null=True, blank=True, db_column='endTime')
    paused = models.BooleanField()
    timestamp_column = models.CharField(max_length=255, null=True, blank=True, db_column='timestampColumn')
    timestamp_format = models.CharField(max_length=255, null=True, blank=True, db_column='timestampFormat')
    timestamp_offset = models.CharField(max_length=255, null=True, blank=True, db_column='timestampOffset')
    data_loader = models.ForeignKey(
        DataLoader, on_delete=models.SET_NULL, null=True, blank=True, db_column='dataLoaderId'
    )
    data_source_thru = models.DateTimeField(null=True, blank=True, db_column='dataSourceThru')
    last_sync_successful = models.BooleanField(null=True, blank=True, db_column='lastSyncSuccessful')
    last_sync_message = models.TextField(null=True, blank=True, db_column='lastSyncMessage')
    last_synced = models.DateTimeField(null=True, blank=True, db_column='lastSynced')
    next_sync = models.DateTimeField(null=True, blank=True, db_column='nextSync')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='data_sources', db_column='personId')
    history = HistoricalRecords(custom_model_name='DataSourceChangeLog', related_name='log')

    class Meta:
        db_table = 'DataSource'


class Datastream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    description = models.TextField()
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, db_column='thingId', related_name='datastreams')
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, db_column='sensorId', related_name='datastreams')
    observed_property = models.ForeignKey(
        ObservedProperty, on_delete=models.PROTECT, db_column='observedPropertyId', related_name='datastreams'
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, db_column='unitId', related_name='datastreams')
    processing_level = models.ForeignKey(
        ProcessingLevel, on_delete=models.PROTECT, db_column='processingLevelId', related_name='datastreams'
    )
    observation_type = models.CharField(max_length=255, db_column='observationType')
    result_type = models.CharField(max_length=255, db_column='resultType')
    status = models.CharField(max_length=255, null=True, blank=True)
    sampled_medium = models.CharField(max_length=255, db_column='sampledMedium')
    value_count = models.IntegerField(null=True, blank=True, db_column='valueCount')
    no_data_value = models.FloatField(db_column='noDataValue')
    intended_time_spacing = models.FloatField(null=True, blank=True, db_column='intendedTimeSpacing')
    intended_time_spacing_units = models.CharField(max_length=255, null=True, blank=True, db_column='intendedTimeSpacingUnits')
    aggregation_statistic = models.CharField(max_length=255, db_column='aggregationStatistic')
    time_aggregation_interval = models.FloatField(db_column='timeAggregationInterval')
    time_aggregation_interval_units = models.ForeignKey(Unit, on_delete=models.PROTECT,
                                                        related_name='time_aggregation_interval_units',
                                                        db_column='timeAggregationIntervalUnitsId')
    phenomenon_begin_time = models.DateTimeField(null=True, blank=True, db_column='phenomenonBeginTime')
    phenomenon_end_time = models.DateTimeField(null=True, blank=True, db_column='phenomenonEndTime')

    is_visible = models.BooleanField(default=True, db_column='isVisible')
    is_data_visible = models.BooleanField(default=True, db_column='isDataVisible')
    data_source = models.ForeignKey(
        DataSource, on_delete=models.SET_NULL, null=True, blank=True, db_column='dataSourceId'
    )
    data_source_column = models.CharField(max_length=255, null=True, blank=True, db_column='dataSourceColumn')

    # In the data model, not implemented for now
    observed_area = models.CharField(max_length=255, null=True, blank=True, db_column='observedArea')
    result_end_time = models.DateTimeField(null=True, blank=True, db_column='resultEndTime')
    result_begin_time = models.DateTimeField(null=True, blank=True, db_column='resultBeginTime')
    history = HistoricalRecords(custom_model_name='DatastreamChangeLog', related_name='log')

    class Meta:
        db_table = 'Datastream'


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


class ResultQualifier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=255)
    description = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='result_qualifiers', null=True,
                               blank=True, db_column='personId')
    history = HistoricalRecords(custom_model_name='ResultQualifierChangeLog', related_name='log')

    def delete(self, using=None, keep_parents=False):
        if Observation.objects.filter(result_qualifiers__contains=[self.id]).exists():
            raise IntegrityError(
                f'Cannot delete result qualifier {str(self.id)} because it is referenced by one or more observations.'
            )
        else:
            super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        db_table = 'ResultQualifier'


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates', db_column='thingId')
    person = ForeignKey(Person, on_delete=models.CASCADE, related_name='thing_associations', db_column='personId')
    owns_thing = models.BooleanField(default=False, db_column='ownsThing')
    follows_thing = models.BooleanField(default=False, db_column='followsThing')
    is_primary_owner = models.BooleanField(default=False, db_column='isPrimaryOwner')
    history = HistoricalRecords(custom_model_name='ThingAssociationChangeLog', related_name='log')

    class Meta:
        db_table = 'ThingAssociation'
        unique_together = ('thing', 'person')
