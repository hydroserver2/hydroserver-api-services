from django.contrib import admin
from etl.models import OrchestrationSystem, DataSource, DataArchive


admin.site.register(OrchestrationSystem)
admin.site.register(DataSource)
admin.site.register(DataArchive)
