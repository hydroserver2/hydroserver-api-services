from django.contrib import admin
from etl.models import OrchestrationSystem, DataSource, DataArchive


class OrchestrationSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system_type", "workspace__name")


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system__name", "workspace__name")


class DataArchiveAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system__name", "workspace__name")


admin.site.register(OrchestrationSystem, OrchestrationSystemAdmin)
admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(DataArchive, DataArchiveAdmin)
