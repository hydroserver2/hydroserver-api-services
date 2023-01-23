from django.contrib import admin

from .models import Thing, Sensor, ObservedProperty, DataStream, Observation, FeatureOfInterest

admin.site.register(Thing)
admin.site.register(Sensor)
admin.site.register(ObservedProperty)
admin.site.register(DataStream)
admin.site.register(Observation)
admin.site.register(FeatureOfInterest)
