import uuid
import pytz
from datetime import datetime
from django.db.models import ForeignKey
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from accounts.models import Person
import boto3
from botocore.exceptions import ClientError
from hydroserver.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME


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

    def __str__(self):
        return self.name

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
    location = models.OneToOneField(Location, related_name='thing', on_delete=models.CASCADE, db_column='locationId')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Thing'


class HistoricalLocation(models.Model):
    thing = models.ForeignKey('Thing', on_delete=models.CASCADE, db_column='thingId')
    time = models.DateTimeField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE, db_column='locationId')

    class Meta:
        db_table = 'HistoricalLocation'


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.ForeignKey('Thing', related_name='photos', on_delete=models.CASCADE, db_column='thingId')
    file_path = models.CharField(max_length=1000, db_column='filePath')
    link = models.URLField(max_length=2000)

    def __str__(self):
        return f'Photo for {self.thing.name}'

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

    file_name = instance.link.split(f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')[1]

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

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ObservedProperty'


class FeatureOfInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255, db_column='encodingType')
    feature = models.TextField()

    class Meta:
        db_table = 'FeatureOfInterest'


class ProcessingLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='processing_levels', null=True,
                               blank=True, db_column='personId')
    code = models.CharField(max_length=255)
    definition = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'ProcessingLevel'


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, db_column='personId')
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    definition = models.TextField()
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Unit'


class DataLoader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='data_loaders')


class DataSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    header_row = models.PositiveIntegerField(null=True, blank=True)
    data_start_row = models.PositiveIntegerField(null=True, blank=True)
    delimiter = models.CharField(max_length=1, null=True, blank=True)
    quote_char = models.CharField(max_length=1, null=True, blank=True)
    interval = models.PositiveIntegerField(null=True, blank=True)
    interval_units = models.CharField(max_length=255, null=True, blank=True)
    crontab = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    paused = models.BooleanField()
    timestamp_column = models.CharField(max_length=255, null=True, blank=True)
    timestamp_format = models.CharField(max_length=255, null=True, blank=True)
    timestamp_offset = models.CharField(max_length=255, null=True, blank=True)
    data_loader = models.ForeignKey(DataLoader, on_delete=models.SET_NULL, null=True, blank=True)
    data_source_thru = models.DateTimeField(null=True, blank=True)
    last_sync_successful = models.BooleanField(null=True, blank=True)
    last_sync_message = models.TextField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    next_sync = models.DateTimeField(null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='data_sources')

    def __str__(self):
        return self.name


class Datastream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.UUIDField()
    description = models.TextField()
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, db_column='sensorId')
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, db_column='thingId')
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.PROTECT, db_column='observedPropertyId')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, db_column='unitId')
    observation_type = models.CharField(max_length=255, db_column='observationType')
    result_type = models.CharField(max_length=255, db_column='resultType')
    status = models.CharField(max_length=255, null=True, blank=True)
    sampled_medium = models.CharField(max_length=255, db_column='sampledMedium')
    value_count = models.IntegerField(null=True, blank=True, db_column='valueCount')
    no_data_value = models.FloatField(db_column='noDataValue')
    processing_level = models.ForeignKey(ProcessingLevel, on_delete=models.PROTECT, db_column='processingLevelId')
    intended_time_spacing = models.FloatField(null=True, blank=True)
    intended_time_spacing_units = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True,
                                                    related_name='intended_time_spacing_units',
                                                    db_column='intendedTimeSpacingUnitsId')
    aggregation_statistic = models.CharField(max_length=255, db_column='aggregationStatistic')
    time_aggregation_interval = models.FloatField(db_column='timeAggregationInterval')
    time_aggregation_interval_units = models.ForeignKey(Unit, on_delete=models.PROTECT,
                                                        related_name='time_aggregation_interval_units',
                                                        db_column='timeAggregationIntervalUnitsId')
    phenomenon_begin_time = models.DateTimeField(null=True, blank=True, db_column='phenomenonBeginTime')
    phenomenon_end_time = models.DateTimeField(null=True, blank=True, db_column='phenomenonEndTime')

    is_visible = models.BooleanField(default=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    data_source_column = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.name = str(self.id)
        self.description = f'{self.observed_property.name} at {self.thing.name} - {self.processing_level.code}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description

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

    def save(self, *args, **kwargs):
        if not self.phenomenon_time:
            self.phenomenon_time = datetime.now(pytz.utc)

    def __str__(self):
        return f'{self.datastream.observed_property.name} at {self.datastream.thing.name} ' + \
               f'on {self.phenomenon_time.strftime("%Y-%m-%d %H:%M:%S")} - {self.datastream.processing_level.code}'

    class Meta:
        db_table = 'Observation'
        managed = False


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates', db_column='thingId')
    person = ForeignKey(Person, on_delete=models.CASCADE, related_name='thing_associations', db_column='personId')
    owns_thing = models.BooleanField(default=False, db_column='ownsThing')
    follows_thing = models.BooleanField(default=False, db_column='followsThing')
    is_primary_owner = models.BooleanField(default=False, db_column='isPrimaryOwner')

    def __str__(self):
        return f'{self.person.first_name} {self.person.last_name} - {self.thing.name}'

    class Meta:
        db_table = 'ThingAssociation'
        unique_together = ('thing', 'person')
