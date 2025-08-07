from django.contrib import admin
from web.models import InstanceConfiguration, MapLayer, ContactInformation


class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ("title", "link")


class MapLayerAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "priority", "source", "attribution")


admin.site.register(InstanceConfiguration)
admin.site.register(MapLayer, MapLayerAdmin)
admin.site.register(ContactInformation, ContactInformationAdmin)
