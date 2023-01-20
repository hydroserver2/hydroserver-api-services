import uuid

from django.db import models


class Thing(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    properties = models.TextField(null=True)


class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    location = models.TextField()
    properties = models.TextField(null=True)
    things = models.ManyToManyField(Thing, related_name='locations')


class HistoricalLocation(models.Model):
    time = models.DateTimeField()
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='historical_locations')
    locations = models.ManyToManyField(Location, related_name='historical_locations')


class Sensor(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    sensor_metadata = models.TextField(null=True)
    properties = models.TextField(null=True)


class ObservedProperty(models.Model):
    name = models.CharField(max_length=255)
    definition = models.TextField()
    description = models.TextField()
    properties = models.TextField(null=True)


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


class Observation(models.Model):
    phenomenon_time = models.DateTimeField()
    result = models.CharField(max_length=255)
    result_time = models.DateTimeField()
    result_quality = models.CharField(max_length=255, null=True)
    valid_time = models.DateTimeField(null=True)
    parameters = models.TextField(null=True)
    datastream = models.ForeignKey(Datastream, on_delete=models.CASCADE)
    feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.CASCADE)
