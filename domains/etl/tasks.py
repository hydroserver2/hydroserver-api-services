import logging
import pandas as pd
from uuid import UUID
from datetime import timedelta
from celery import shared_task
from pydantic import TypeAdapter
from celery.signals import task_prerun, task_success, task_failure, task_postrun
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.management import call_command
from domains.etl.models import Task, TaskRun
from .loader import HydroServerInternalLoader
from hydroserverpy.etl.factories import extractor_factory, transformer_factory
from hydroserverpy.etl.etl_configuration import ExtractorConfig, TransformerConfig, SourceTargetMapping, MappingPath


@shared_task(bind=True, expires=10)
def run_etl_task(self, task_id: str):
    """
    Runs a HydroServer ETL task based on the task configuration provided.
    """

    task = Task.objects.select_related(
        "data_connection"
    ).prefetch_related(
        "mappings", "mappings__paths"
    ).get(pk=UUID(task_id))

    extractor_cls = extractor_factory(TypeAdapter(ExtractorConfig).validate_python({
        "type": task.data_connection.extractor_type,
        **task.data_connection.extractor_settings
    }))
    transformer_cls = transformer_factory(TypeAdapter(TransformerConfig).validate_python({
        "type": task.data_connection.transformer_type,
        **task.data_connection.transformer_settings
    }))
    loader_cls = HydroServerInternalLoader(task)

    task_mappings = [
        SourceTargetMapping(
            source_identifier=task_mapping.source_identifier,
            paths=[
                MappingPath(
                    target_identifier=task_mapping_path.target_identifier,
                    data_transformations=task_mapping_path.data_transformations,
                ) for task_mapping_path in task_mapping.paths.all()
            ]
        ) for task_mapping in task.mappings.all()
    ]

    logging.info("Starting extract")
    data = extractor_cls.extract(task, loader_cls)
    if data is None or (isinstance(data, pd.DataFrame) and data.empty):
        return {"message": f"No data returned from the extractor for task: {str(task.id)}"}

    logging.info("Starting transform")
    data = transformer_cls.transform(data, task_mappings)
    if data is None or (isinstance(data, pd.DataFrame) and data.empty):
        return {"message": f"No data returned from the transformer for task: {str(task.id)}"}

    logging.info("Starting load")
    loader_cls.load(data, task)

    return {"message": f"Finished processing task: {str(task.id)}"}


@task_prerun.connect
def mark_etl_task_started(sender, task_id, kwargs, **extra):
    """
    Marks an ETL task as RUNNING.
    """

    if sender != run_etl_task:
        return

    try:
        TaskRun.objects.create(
            id=task_id,
            task_id=kwargs["task_id"],
            status="RUNNING",
            started_at=timezone.now(),
        )
    except IntegrityError:
        return


@task_postrun.connect
def update_next_run(sender, task_id, kwargs, **extra):
    if sender != run_etl_task:
        return

    try:
        task = Task.objects.select_related("periodic_task").get(
            pk=kwargs["task_id"]
        )
    except Task.DoesNotExist:
        return

    if not task.periodic_task:
        task.next_run_at = None
        task.save(update_fields=["next_run_at"])
        return

    now = timezone.now()

    time_delta = task.periodic_task.schedule.remaining_estimate(now)
    time_delta = max(time_delta, timedelta(0))

    task.next_run_at = now + time_delta
    task.save(update_fields=["next_run_at"])


@task_success.connect
def mark_etl_task_success(sender, result, **extra):
    """
    Marks an ETL task as SUCCESS.
    """

    if sender != run_etl_task:
        return

    try:
        task_run = TaskRun.objects.get(id=sender.request.id)
    except TaskRun.DoesNotExist:
        return

    task_run.status = "SUCCESS"
    task_run.finished_at = timezone.now()
    task_run.result = result

    task_run.save(update_fields=["status", "finished_at", "result"])


@task_failure.connect
def mark_etl_task_failure(sender, task_id, einfo, exception, **extra):
    """
    Marks an ETL task as FAILED.
    """

    if sender != run_etl_task:
        return

    try:
        task_run = TaskRun.objects.get(id=task_id)
    except TaskRun.DoesNotExist:
        return

    task_run.status = "FAILURE"
    task_run.finished_at = timezone.now()
    task_run.result = {
        "error": str(exception),
        "traceback": einfo.traceback,
    }

    task_run.save(update_fields=["status", "finished_at", "result"])


@shared_task(bind=True, expires=10)
def cleanup_etl_task_runs(self, days=14):
    """
    Celery task to run the cleanup_etl_task_runs management command.
    """

    call_command("cleanup_etl_task_runs", f"--days={days}")
