from django.contrib import admin
from etl.models import OrchestrationSystem, DataSource, DataArchive


class OrchestrationSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system_type", "workspace__name")

    def delete_queryset(self, request, queryset):
        OrchestrationSystem.delete_contents(filter_arg=queryset, filter_suffix="in")
        queryset.delete()


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system__name", "workspace__name")

    def delete_queryset(self, request, queryset):
        DataSource.delete_contents(filter_arg=queryset, filter_suffix="in")
        queryset.delete()


class DataArchiveAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system__name", "workspace__name")

    def delete_queryset(self, request, queryset):
        DataArchive.delete_contents(filter_arg=queryset, filter_suffix="in")
        queryset.delete()


admin.site.register(OrchestrationSystem, OrchestrationSystemAdmin)
admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(DataArchive, DataArchiveAdmin)
