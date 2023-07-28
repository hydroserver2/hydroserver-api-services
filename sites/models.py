import uuid

from django.db.models import ForeignKey
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from accounts.models import CustomUser
import boto3
from botocore.exceptions import ClientError
from hydroserver.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME

class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    sampling_feature_type = models.CharField(max_length=200, null=True, blank=True)  # CV Table?
    sampling_feature_code = models.CharField(max_length=200, null=True, blank=True)
    site_type = models.CharField(max_length=200, null=True, blank=True)  # CV Table?
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.ForeignKey('Thing', related_name='photos', on_delete=models.CASCADE)
    url = models.URLField(max_length=2000)

    def __str__(self):
        return f'Photo for {self.thing.name}'
        

@receiver(pre_delete, sender=Photo)
def delete_photo(sender, instance, **kwargs):
    print("deleting photo")
    s3 = boto3.client('s3', 
                        region_name='us-east-1', 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    file_name = instance.url.split(f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/")[1]

    try:
        s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_name)
    except ClientError as e:
        print(f"Error deleting {file_name} from S3: {e}")


class Location(models.Model):
    thing = models.OneToOneField(Thing, primary_key=True, related_name='location', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    elevation = models.DecimalField(max_digits=22, decimal_places=16)
    elevation_datum = models.CharField(max_length=255)  # CV Table?
    city = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    county = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    encoding_type = models.CharField(max_length=255, blank=True, null=True)  # CV Table or constant?
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    model_url = models.CharField(max_length=500, null=True, blank=True)
    method_type = models.CharField(max_length=100, blank=True, null=True)
    method_link = models.CharField(max_length=500, blank=True, null=True)
    method_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self.method_type and self.method_type.strip().lower().replace(" ", "") == 'instrumentdeployment':
            return f"{self.manufacturer}:{self.model}"
        else:
            return f"{self.method_type}:{self.method_code}"


class ObservedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    definition = models.TextField()
    description = models.TextField()
    variable_type = models.CharField(max_length=50, blank=True, null=True)
    variable_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class FeatureOfInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    feature = models.TextField()


class ProcessingLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='processing_levels', null=True, blank=True)
    processing_level_code = models.CharField(max_length=255)
    definition = models.TextField()
    explanation = models.TextField()

    def __str__(self):
        return self.processing_level_code


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=50)
    definition = models.TextField()
    unit_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DataLoader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)


class DataLoaderOwner(models.Model):
    data_loader = ForeignKey(DataLoader, on_delete=models.CASCADE)
    person = ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_primary_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person.first_name} {self.person.last_name} - {self.data_loader.name}"

    class Meta:
        unique_together = ("data_loader", "person")


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

    def __str__(self):
        return self.name


class DataSourceOwner(models.Model):
    data_source = ForeignKey(DataSource, on_delete=models.CASCADE)
    person = ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_primary_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person.first_name} {self.person.last_name} - {self.data_source.name}"

    class Meta:
        unique_together = ("data_source", "person")


class Datastream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='datastreams')
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, related_name='datastreams')
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True)
    processing_level = models.ForeignKey(ProcessingLevel, on_delete=models.PROTECT, null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    observation_type = models.CharField(max_length=255, null=True, blank=True)  # CV Table?
    result_type = models.CharField(max_length=255, null=True, blank=True)  # CV Table?
    status = models.CharField(max_length=255, null=True, blank=True)  # CV Table?
    sampled_medium = models.CharField(max_length=255, null=True, blank=True)  # CV Table?
    value_count = models.IntegerField(null=True, blank=True)
    no_data_value = models.FloatField(max_length=255, null=True, blank=True)
    intended_time_spacing = models.FloatField(max_length=255, null=True, blank=True)
    intended_time_spacing_units = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True,
                                                    related_name='intended_time_spacing')
    aggregation_statistic = models.CharField(max_length=255, null=True, blank=True)  # CV Table?
    time_aggregation_interval = models.FloatField(max_length=255, null=True, blank=True)
    time_aggregation_interval_units = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True,
                                                        related_name='time_aggregation_interval')
    # observed_area = models.TextField(null=True)
    phenomenon_start_time = models.DateTimeField(null=True, blank=True)
    phenomenon_end_time = models.DateTimeField(null=True, blank=True)
    result_begin_time = models.DateTimeField(null=True, blank=True)
    result_end_time = models.DateTimeField(null=True, blank=True)

    is_visible = models.BooleanField(default=True)

    data_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    data_source_column = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = str(self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datastream = models.ForeignKey(Datastream, on_delete=models.CASCADE)
    result = models.FloatField()
    result_time = models.DateTimeField()
    result_quality = models.CharField(max_length=255, null=True)  # CV Table?
    phenomenon_time = models.DateTimeField(null=True, blank=True)
    valid_begin_time = models.DateTimeField(null=True, blank=True)
    valid_end_time = models.DateTimeField(null=True, blank=True)
    # feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.CASCADE)

    class Meta:
        managed = False

    def __str__(self):
        name = f"{self.datastream.thing.name}: {self.datastream.observed_property.name}"
        if hasattr(self.phenomenon_time, 'strftime'):
            name += f" - {self.phenomenon_time.strftime('%Y-%m-%d %H:%M:%S')}"
        return name


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates')
    person = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='thing_associations')
    owns_thing = models.BooleanField(default=False)
    follows_thing = models.BooleanField(default=False)
    is_primary_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person.first_name} {self.person.last_name} - {self.thing.name}"

    class Meta:
        unique_together = ("thing", "person")


# class HistoricalLocation(models.Model):
#     time = models.DateTimeField()
#     thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='historical_locations')
#     locations = models.ManyToManyField(Location, related_name='historical_locations')
