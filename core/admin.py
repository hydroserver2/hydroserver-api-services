from django.contrib import admin
from .models import Thing, Sensor, ObservedProperty, Datastream, \
    Observation, FeatureOfInterest, Location, ThingAssociation, Unit, ProcessingLevel, Photo

admin.site.register(Thing)
admin.site.register(Sensor)
admin.site.register(ObservedProperty)
admin.site.register(Datastream)
admin.site.register(Observation)
admin.site.register(FeatureOfInterest)
admin.site.register(Location)
admin.site.register(ThingAssociation)
admin.site.register(Unit)
admin.site.register(ProcessingLevel)
admin.site.register(Photo)
