import uuid6
from django.db import models
from .task import Task
from domains.etl.run_result_normalizer import normalize_task_run_result, task_transformer_raw


class TaskRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        transformer_raw = task_transformer_raw(self.task) if self.task_id else None
        self.result = normalize_task_run_result(
            status=self.status,
            result=self.result,
            transformer_raw=transformer_raw,
        )
        super().save(*args, **kwargs)
