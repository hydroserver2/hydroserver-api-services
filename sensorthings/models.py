from django.db import models


# TODO: Figure out where to put these utils.
class SensorThingsUtils:
    def get_ref(self, request):
        return f'{request.get_host()}{request.path_info}({self.id})'


class Thing(models.Model, SensorThingsUtils):
    name = models.CharField(max_length=255)
    description = models.TextField()
    properties = models.TextField(null=True)


class Location(models.Model, SensorThingsUtils):
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    location = models.TextField()
    properties = models.TextField(null=True)
    things = models.ManyToManyField(Thing)


class HistoricalLocation(models.Model, SensorThingsUtils):
    time = models.DateTimeField()
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)


class Sensor(models.Model, SensorThingsUtils):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    sensor_metadata = models.TextField(null=True)
    properties = models.TextField(null=True)


class ObservedProperty(models.Model, SensorThingsUtils):
    name = models.CharField(max_length=255)
    definition = models.TextField()
    description = models.TextField()
    properties = models.TextField(null=True)


class FeatureOfInterest(models.Model, SensorThingsUtils):
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255)
    feature = models.TextField()
    properties = models.TextField(null=True)


class DataStream(models.Model, SensorThingsUtils):
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_of_measurement = models.TextField()
    observation_type = models.CharField(max_length=255)
    properties = models.TextField(null=True)
    observed_area = models.TextField(null=True)
    phenomenon_time = models.DateTimeField(null=True)
    result_time = models.DateTimeField(null=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.CASCADE)


class Observation(models.Model, SensorThingsUtils):
    result = models.CharField(max_length=255)
    result_time = models.DateTimeField()
    result_quality = models.CharField(max_length=255, null=True)
    valid_time = models.DateTimeField(null=True)
    properties = models.TextField(null=True)
    data_stream = models.ForeignKey(DataStream, on_delete=models.CASCADE)
    feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.CASCADE)
