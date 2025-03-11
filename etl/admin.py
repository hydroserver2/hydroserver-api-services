from django.contrib import admin
from etl.models import EtlSystemPlatform, EtlSystem, EtlConfiguration, DataSource, LinkedDatastream


admin.site.register(EtlSystemPlatform)
admin.site.register(EtlSystem)
admin.site.register(EtlConfiguration)
admin.site.register(DataSource)
admin.site.register(LinkedDatastream)
