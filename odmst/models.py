import uuid
from django.db import models


class OrganizationTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class MethodTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class SamplingFeatureTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class SiteTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class ElevationDatumCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class ObservationTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class ResultTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class StatusCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class SampledMediumCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class AggregationStatisticCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class UnitTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class VariableTypeCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class ResultQualityCv(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField()
    link = models.TextField(blank=True, null=True)


class Thing(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    sampling_feature_type = models.ForeignKey(SamplingFeatureTypeCv, on_delete=models.PROTECT)
    site_type = models.ForeignKey(SiteTypeCv, on_delete=models.PROTECT)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    elevation_m = models.FloatField(blank=True, null=True)
    elevation_datum = models.ForeignKey(ElevationDatumCv, on_delete=models.PROTECT)
    state = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)


class SensorModel(models.Model):
    name = models.CharField(max_length=255)
    link = models.TextField(blank=True, null=True)
    manufacturer_name = models.CharField(max_length=255)


class Sensor(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.TextField()
    description = models.TextField()
    link = models.TextField(blank=True, null=True)
    method_type = models.ForeignKey(MethodTypeCv, on_delete=models.PROTECT)


class ProcessingLevel(models.Model):
    code = models.CharField(max_length=255)
    definition = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)


class Unit(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.TextField()
    definition = models.TextField()
    unit_type = models.ForeignKey(UnitTypeCv, on_delete=models.PROTECT)


class ObservedProperty(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    definition = models.TextField()
    description = models.TextField()
    variable_type = models.ForeignKey(VariableTypeCv, on_delete=models.PROTECT)


class Datastream(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    thing = models.ForeignKey(Thing, on_delete=models.PROTECT)
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)
    observed_property = models.ForeignKey(ObservedProperty, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    observation_type = models.ForeignKey(ObservationTypeCv, on_delete=models.PROTECT)
    result_type = models.ForeignKey(ResultTypeCv, on_delete=models.PROTECT)
    status = models.ForeignKey(StatusCv, on_delete=models.PROTECT, blank=True, null=True)
    sampled_medium = models.ForeignKey(SampledMediumCv, on_delete=models.PROTECT)
    value_count = models.IntegerField(blank=True, null=True)
    no_data_value = models.DecimalField(max_digits=22, decimal_places=16)
    processing_level = models.ForeignKey(ProcessingLevel, on_delete=models.PROTECT)
    intended_time_spacing = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    intended_time_spacing_unit = models.ForeignKey(Unit, blank=True, null=True,
                                                   related_name='intended_time_spacing_unit', on_delete=models.PROTECT)
    aggregation_statistic = models.ForeignKey(AggregationStatisticCv, on_delete=models.PROTECT)
    time_aggregation_interval = models.DecimalField(max_digits=22, decimal_places=16)
    time_aggregation_interval_unit = models.ForeignKey(Unit, related_name='time_aggregation_interval_unit',
                                                       on_delete=models.PROTECT)
    phenomenon_begin_time = models.DateTimeField(blank=True, null=True)
    phenomenon_end_time = models.DateTimeField(blank=True, null=True)


class Observation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    datastream = models.ForeignKey(Datastream, on_delete=models.PROTECT)
    phenomenon_time = models.DateTimeField()
    result = models.DecimalField(max_digits=22, decimal_places=16)
    result_quality = models.ForeignKey(ResultQualityCv, blank=True, null=True, on_delete=models.PROTECT)
    valid_begin_time = models.DateTimeField(blank=True, null=True)
    valid_end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
