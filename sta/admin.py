from django.contrib import admin
from django.db import transaction
from django.core.management.base import CommandError
from sta.models import (Thing, Sensor, ObservedProperty, Datastream, Location, Unit, ProcessingLevel,
                        Photo, Tag, ResultQualifier, Observation)
from sta.management.utils import generate_test_timeseries


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

    actions = ["populate_with_test_observations", "delete_observations"]

    def populate_with_test_observations(self, request, queryset):
        if request.user.is_superuser:
            with transaction.atomic():
                try:
                    for datastream in queryset:
                        generate_test_timeseries(datastream.id)
                except CommandError as e:
                    self.message_user(request, f"An error occurred: {str(e)}", level="error")
            self.message_user(request, "Observations loaded successfully.")
        else:
            self.message_user(request, "You do not have permission to perform this action", level="error")

    def delete_observations(self, request, queryset):
        if request.user.is_superuser:
            with transaction.atomic():
                for datastream in queryset:
                    observations = Observation.objects.filter(datastream_id=datastream.id)
                    observations.delete()
            self.message_user(request, "Observations deleted successfully.")
        else:
            self.message_user(request, "You do not have permission to perform this action", level="error")

    populate_with_test_observations.short_description = "Populate with test observations"
    delete_observations.short_description = "Delete datastream observations"


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
