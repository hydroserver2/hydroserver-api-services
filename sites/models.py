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


class HistoricalLocation(models.Model):
    time = models.DateTimeField()
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='historical_locations')
    locations = models.ManyToManyField(Location, related_name='historical_locations')


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    sensor_metadata = models.TextField(null=True)
    properties = models.TextField(null=True)

    def __str__(self):
        return self.name


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
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Observation(models.Model):
    phenomenon_time = models.DateTimeField()
    result = models.CharField(max_length=255)
    result_time = models.DateTimeField()
    result_quality = models.CharField(max_length=255, null=True)
    valid_time = models.DateTimeField(null=True)
    parameters = models.TextField(null=True)
    datastream = models.ForeignKey(Datastream, on_delete=models.CASCADE)
    feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.datastream.thing.name}: " \
               f"{self.datastream.observed_property.name} - {self.result_time.strftime('%Y-%m-%d %H:%M:%S')}"


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates')
    person = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='thing_associations')
    owns_thing = models.BooleanField(default=False)
    follows_thing = models.BooleanField(default=False)

    class Meta:
        unique_together = ("thing", "person")


class SensorManufacturer(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name


class SensorModel(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    manufacturer = models.ForeignKey(SensorManufacturer, on_delete=models.CASCADE)
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE, related_name='model')

    def __str__(self):
        return self.name


# class Site(models.Model):
#     # This model should only contain the data related to how a Thing will be managed
#     name = models.CharField(max_length=200)
#     latitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     longitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     elevation = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     # registration_date = models.DateTimeField(auto_now_add=True)
#     # id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

# class SensorAssociation(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
#     custom_manufacturer = models.CharField(max_length=255, null=True, blank=True)
#     custom_model = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         unique_together = ("user", "sensor")
#
#     def get_manufacturer_model(self):
#         if self.custom_manufacturer and self.custom_model:
#             return f"{self.custom_manufacturer} {self.custom_model}"
#         else:
#             return self.sensor.get_manufacturer_model()
#
#     def __str__(self):
#         return f"{self.sensor} ({self.user})"
