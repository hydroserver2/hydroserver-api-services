from django.contrib import admin
from .models import SensorModel, SensorManufacturer, \
    Thing, Sensor, ObservedProperty, Datastream, Observation, FeatureOfInterest, Location, ThingAssociation

admin.site.register(Thing)
admin.site.register(Sensor)
admin.site.register(ObservedProperty)
admin.site.register(Datastream)
admin.site.register(Observation)
admin.site.register(FeatureOfInterest)
admin.site.register(Location)
admin.site.register(SensorModel)
admin.site.register(SensorManufacturer)
admin.site.register(ThingAssociation)
