import logging
import pandas as pd
from uuid import UUID
from celery import shared_task
from pydantic import TypeAdapter
from celery.signals import task_prerun, task_success, task_failure
from django.utils import timezone
from django.db.utils import IntegrityError
from etl.models import Task, TaskRun
from etl.services.loader import HydroServerInternalLoader
from hydroserverpy.etl.factories import extractor_factory, transformer_factory
from hydroserverpy.etl.etl_configuration import ExtractorConfig, TransformerConfig, SourceTargetMapping, MappingPath


@shared_task(bind=True, expires=10)
def run_etl_task(self, task_id: str):
    """"""

    task = Task.objects.select_related(
        "job"
    ).prefetch_related(
        "mappings", "mappings__paths"
    ).get(pk=UUID(task_id))

    extractor_cls = extractor_factory(TypeAdapter(ExtractorConfig).validate_python({
        "type": task.job.extractor_type,
        **task.job.extractor_settings
    }))
    transformer_cls = transformer_factory(TypeAdapter(TransformerConfig).validate_python({
        "type": task.job.transformer_type,
        **task.job.transformer_settings
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


@task_success.connect
def mark_etl_task_success(sender, result, **extra):
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
