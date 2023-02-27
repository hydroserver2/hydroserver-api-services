import uuid

from django.db.models import ForeignKey
from django.db import models

from accounts.models import CustomUser


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    properties = models.TextField(null=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField()
    city = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    properties = models.TextField(null=True, blank=True)
    thing = models.OneToOneField(Thing, related_name='location', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    encoding_type = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    method_type = models.CharField(max_length=100, blank=True, null=True)
    method_link = models.CharField(max_length=500, blank=True, null=True)
    method_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self.method_type == 'instrumentDeployment':
            return f"{self.manufacturer}:{self.model}"
        else:
            return f"{self.method_type}:{self.method_code}"


class ObservedProperty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    definition = models.TextField()
    description = models.TextField()
    properties = models.TextField(null=True)

    def __str__(self):
        return self.name


class FeatureOfInterest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    feature = models.TextField()
    properties = models.TextField(null=True)


class Datastream(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_of_measurement = models.TextField()
    observation_type = models.CharField(max_length=255)
    properties = models.TextField(null=True)
    observed_area = models.TextField(null=True)
    phenomenon_time = models.DateTimeField(null=True)
    result_time = models.DateTimeField(null=True)
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='datastreams')
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='datastreams')
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Observation(models.Model):
    phenomenon_time = models.DateTimeField()
    result = models.CharField(max_length=255)
    result_time = models.DateTimeField(null=True)
    result_quality = models.CharField(max_length=255, null=True)
    valid_time = models.DateTimeField(null=True)
    parameters = models.TextField(null=True)
    datastream = models.ForeignKey(Datastream, on_delete=models.CASCADE)
    # feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.datastream.thing.name}: " \
               f"{self.datastream.observed_property.name} - {self.phenomenon_time.strftime('%Y-%m-%d %H:%M:%S')}"


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates')
    person = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='thing_associations')
    owns_thing = models.BooleanField(default=False)
    follows_thing = models.BooleanField(default=False)

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

