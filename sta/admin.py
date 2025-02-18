from django.contrib import admin
from sta.models import (Thing, Sensor, ObservedProperty, Datastream, Location, Unit, ProcessingLevel,
                        Photo, Tag, ResultQualifier)


admin.site.register(Thing)
admin.site.register(Sensor)
admin.site.register(ObservedProperty)
admin.site.register(Datastream)
admin.site.register(Location)
admin.site.register(Unit)
admin.site.register(ProcessingLevel)
admin.site.register(Photo)
admin.site.register(Tag)
admin.site.register(ResultQualifier)
