from django.db import models


class OrchestrationConfiguration(models.Model):
    interval = models.PositiveIntegerField(blank=True, null=True)
    interval_units = models.CharField(max_length=255, blank=True, null=True)
    crontab = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    paused = models.BooleanField(default=False)
    last_run_successful = models.BooleanField(blank=True, null=True)
    last_run_message = models.TextField(blank=True, null=True)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
