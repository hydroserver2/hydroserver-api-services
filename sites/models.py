import uuid

from django.db.models import ForeignKey
from django.db import models

from accounts.models import CustomUser


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    sampling_feature_type = models.CharField(max_length=200, null=True, blank=True)  # CV Table?
    sampling_feature_code = models.CharField(max_length=200, null=True, blank=True)
    site_type = models.CharField(max_length=200, null=True, blank=True)  # CV Table?

    def __str__(self):
        return self.name


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
    country = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    definition = models.TextField()
    description = models.TextField()
    variable_type = models.CharField(max_length=50, blank=True, null=True)
    variable_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class FeatureOfInterest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    feature = models.TextField()


class ProcessingLevel(models.Model):
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='processing_levels')
    processing_level_code = models.CharField(max_length=255)
    definition = models.TextField()
    explanation = models.TextField()

    def __str__(self):
        return self.processing_level_code


class Unit(models.Model):
    name = models.CharField(max_length=100)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=50)
    definition = models.TextField()
    unit_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Datastream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='datastreams')
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='datastreams')
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.CASCADE)
    processing_level = models.ForeignKey(ProcessingLevel, on_delete=models.SET_NULL, null=True, blank=True)

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
        return f"{self.datastream.thing.name}: " \
               f"{self.datastream.observed_property.name} - {self.phenomenon_time.strftime('%Y-%m-%d %H:%M:%S')}"


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates')
    person = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='thing_associations')
    owns_thing = models.BooleanField(default=False)
    follows_thing = models.BooleanField(default=False)
    is_primary_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = ("thing", "person")


# class HistoricalLocation(models.Model):
#     time = models.DateTimeField()
#     thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='historical_locations')
#     locations = models.ManyToManyField(Location, related_name='historical_locations')

# class Site(models.Model):
#     # This model should only contain the data related to how a Thing will be managed
#     name = models.CharField(max_length=200)
#     latitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     longitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     elevation = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     # registration_date = models.DateTimeField(auto_now_add=True)
#     # id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

