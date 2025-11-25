from uuid import UUID
from celery import shared_task
from celery.signals import task_prerun, task_success, task_failure
from django.utils import timezone
from django.db.utils import IntegrityError
from etl.models import Task, TaskRun
# from hydroserverpy.api.services import etl


@shared_task(bind=True, expires=10)
def run_etl_task(self, task_id: str):
    """"""

    task = Task.objects.select_related(
        "job"
    ).prefetch_related(
        "mappings", "mappings__paths"
    ).get(pk=UUID(task_id))

    # TODO: ETL factory logic goes here

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
