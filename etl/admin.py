from django.contrib import admin
from etl.models import OrchestrationSystem, Job, Task, TaskMapping, TaskMappingPath, TaskRun


class OrchestrationSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "orchestration_system_type", "workspace__name")


class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "job_type", "workspace__name")


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "job__name", "orchestration_system__name", "job__workspace__name")


class TaskMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "task__name", "source_identifier", "task__job__name", "task__job__workspace__name")


class TaskMappingPathAdmin(admin.ModelAdmin):
    list_display = ("id", "task_mapping__task__name", "target_identifier", "task_mapping__task__job__name",
                    "task_mapping__task__job__workspace__name")


class TaskRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "started_at", "finished_at", "result")


admin.site.register(OrchestrationSystem, OrchestrationSystemAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskMapping, TaskMappingAdmin)
admin.site.register(TaskMappingPath, TaskMappingPathAdmin)
admin.site.register(TaskRun, TaskRunAdmin)
