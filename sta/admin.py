from django.contrib import admin
from sta.models import (Thing, Sensor, ObservedProperty, Datastream, Location, Unit, ProcessingLevel,
                        Photo, Tag, ResultQualifier)


class ThingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace__name", "is_private")


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "thing__name", "thing__workspace__name")


class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "thing__name", "thing__workspace__name")


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "value", "thing__name", "thing__workspace__name")


class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace__name")


class ObservedPropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace__name")


class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace__name")


class ProcessingLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "workspace__name")


class DatastreamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "thing__name", "thing__workspace__name", "is_private")

    # def delete_queryset(self, request, queryset):
    #     for obj in queryset:
    #         obj.delete()


class ResultQualifierAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "workspace__name")


admin.site.register(Thing, ThingAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(ObservedProperty, ObservedPropertyAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(ProcessingLevel, ProcessingLevelAdmin)
admin.site.register(Datastream, DatastreamAdmin)
admin.site.register(ResultQualifier, ResultQualifierAdmin)
