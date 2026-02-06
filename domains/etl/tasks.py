import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any, Optional
from uuid import UUID
import pandas as pd
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


@dataclass
class TaskRunContext:
    stage: str = "setup"
    runtime_source_uri: Optional[str] = None
    stats: dict[str, Any] = field(default_factory=dict)
    log_handler: Optional["TaskLogHandler"] = None


class TaskLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        path = (record.pathname or "").replace("\\", "/")
        return "/hydroserverpy/" in path or "/domains/etl/" in path


class TaskLogHandler(logging.Handler):
    def __init__(self, context: TaskRunContext):
        super().__init__(level=logging.INFO)
        self.context = context
        self.lines: list[str] = []
        self.entries: list[dict[str, Any]] = []
        self._formatter = logging.Formatter()

    def emit(self, record: logging.LogRecord) -> None:
        if not self.filter(record):
            return

        timestamp = datetime.fromtimestamp(
            record.created, tz=dt_timezone.utc
        ).isoformat()
        message = record.getMessage()
        line = f"{timestamp} {record.levelname:<8} {message}"
        if record.exc_info:
            line = f"{line}\n{self._formatter.formatException(record.exc_info)}"
        self.lines.append(line)

        entry: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        if record.exc_info:
            entry["exception"] = self._formatter.formatException(record.exc_info)
        self.entries.append(entry)

        self._capture_runtime_uri(message)

    def _capture_runtime_uri(self, message: str) -> None:
        if self.context.runtime_source_uri:
            return
        if "Resolved runtime source URI:" in message:
            self.context.runtime_source_uri = message.split(
                "Resolved runtime source URI:", 1
            )[1].strip()
            return
        if "Requesting data from" in message:
            if "→" in message:
                self.context.runtime_source_uri = message.split("→", 1)[1].strip()
                return
            if "from" in message:
                self.context.runtime_source_uri = message.split("from", 1)[1].strip()

    def as_text(self) -> str:
        return "\n".join(self.lines).strip()


TASK_RUN_CONTEXT: dict[str, TaskRunContext] = {}


@contextmanager
def capture_task_logs(context: TaskRunContext):
    logger = logging.getLogger()
    handler = TaskLogHandler(context)
    handler.addFilter(TaskLogFilter())
    context.log_handler = handler

    previous_level = logger.level
    if previous_level > logging.INFO:
        logger.setLevel(logging.INFO)

    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.removeHandler(handler)
        if previous_level > logging.INFO:
            logger.setLevel(previous_level)


def _is_empty(data: Any) -> bool:
    if data is None:
        return True
    if isinstance(data, pd.DataFrame) and data.empty:
        return True
    return False


def _describe_payload(data: Any) -> dict[str, Any]:
    if isinstance(data, pd.DataFrame):
        return {
            "type": "DataFrame",
            "rows": len(data),
            "columns": len(data.columns),
        }
    return {"type": type(data).__name__}


def _describe_transformed_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        return {"type": type(data).__name__}
    datastreams = [col for col in data.columns if col != "timestamp"]
    return {
        "type": "DataFrame",
        "rows": len(data),
        "columns": len(data.columns),
        "datastreams": len(datastreams),
    }


def _success_message(stats: dict[str, Any]) -> str:
    load_stats = stats.get("load") or {}
    loaded = load_stats.get("observations_loaded")
    datastreams_loaded = load_stats.get("datastreams_loaded")
    available = load_stats.get("observations_available")
    timestamps_after_cutoff = load_stats.get("timestamps_after_cutoff")
    timestamps_total = load_stats.get("timestamps_total")

    if loaded is not None:
        if loaded == 0:
            if timestamps_total and timestamps_after_cutoff == 0:
                cutoff = load_stats.get("cutoff")
                if cutoff:
                    return (
                        "No new observations to load "
                        f"(all timestamps were at or before {cutoff})."
                    )
                return "No new observations to load (all timestamps were at or before the cutoff)."
            if available == 0:
                return "No new observations to load."
            return "No new observations were loaded."

        if datastreams_loaded is not None:
            return (
                f"Load completed successfully ({loaded} rows across {datastreams_loaded} datastreams)."
            )
        return f"Load completed successfully ({loaded} rows loaded)."

    transform_stats = stats.get("transform") or {}
    rows = transform_stats.get("rows")
    datastreams = transform_stats.get("datastreams")
    if rows is not None and datastreams is not None:
        return (
            f"Load completed successfully ({rows} rows across {datastreams} datastreams)."
        )
    if rows is not None:
        return f"Load completed successfully ({rows} rows processed)."
    return "Load completed successfully."


def _apply_runtime_uri_aliases(result: dict[str, Any], runtime_source_uri: str) -> None:
    result.setdefault("runtime_source_uri", runtime_source_uri)
    result.setdefault("runtimeSourceUri", runtime_source_uri)
    result.setdefault("runtime_url", runtime_source_uri)
    result.setdefault("runtimeUrl", runtime_source_uri)


def _apply_log_aliases(result: dict[str, Any]) -> None:
    if "log_entries" in result and "logEntries" not in result:
        result["logEntries"] = result["log_entries"]


def _merge_result_with_context(
    result: dict[str, Any], context: Optional[TaskRunContext]
) -> dict[str, Any]:
    if "summary" not in result and "message" in result:
        result["summary"] = result["message"]

    if context:
        if context.runtime_source_uri and not (
            result.get("runtime_source_uri")
            or result.get("runtimeSourceUri")
            or result.get("runtime_url")
            or result.get("runtimeUrl")
        ):
            _apply_runtime_uri_aliases(result, context.runtime_source_uri)

        if context.log_handler:
            if "logs" not in result:
                logs_text = context.log_handler.as_text()
                if logs_text:
                    result["logs"] = logs_text
            if "log_entries" not in result and context.log_handler.entries:
                result["log_entries"] = context.log_handler.entries

        if context.stats and "stats" not in result:
            result["stats"] = context.stats

    _apply_log_aliases(result)
    return result


def _build_task_result(
    message: str,
    context: Optional[TaskRunContext] = None,
    *,
    stage: Optional[str] = None,
    error: Optional[str] = None,
    traceback: Optional[str] = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"message": message, "summary": message}
    if stage:
        result["stage"] = stage
    if error:
        result.update(
            {
                "error": error,
                "failure_reason": error,
                "failureReason": error,
            }
        )
    if traceback:
        result["traceback"] = traceback

    if context and context.runtime_source_uri:
        _apply_runtime_uri_aliases(result, context.runtime_source_uri)

    if context and context.log_handler:
        logs_text = context.log_handler.as_text()
        if logs_text:
            result["logs"] = logs_text
        if context.log_handler.entries:
            result["log_entries"] = context.log_handler.entries

    if context and context.stats:
        result["stats"] = context.stats

    _apply_log_aliases(result)
    return result

@shared_task(bind=True, expires=10, name="etl.tasks.run_etl_task")
def run_etl_task(self, task_id: str):
    """
    Runs a HydroServer ETL task based on the task configuration provided.
    """

    task_run_id = self.request.id
    context = TaskRunContext()
    TASK_RUN_CONTEXT[task_run_id] = context

    with capture_task_logs(context):
        try:
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

            context.stage = "extract"
            logging.info("Starting extract")
            data = extractor_cls.extract(task, loader_cls)
            context.runtime_source_uri = (
                getattr(extractor_cls, "runtime_source_uri", None)
                or context.runtime_source_uri
            )
            context.stats["extract"] = _describe_payload(data)
            if _is_empty(data):
                return _build_task_result(
                    "No data returned from the extractor. Nothing to load.",
                    context,
                    stage=context.stage,
                )

            context.stage = "transform"
            logging.info("Starting transform")
            data = transformer_cls.transform(data, task_mappings)
            context.stats["transform"] = _describe_transformed_data(data)
            if _is_empty(data):
                return _build_task_result(
                    "Transform produced no rows. Nothing to load.",
                    context,
                    stage=context.stage,
                )

            context.stage = "load"
            logging.info("Starting load")
            load_stats = loader_cls.load(data, task)
            if isinstance(load_stats, dict):
                context.stats["load"] = load_stats
            else:
                context.stats["load"] = _describe_transformed_data(data)

            return _build_task_result(
                _success_message(context.stats),
                context,
                stage=context.stage,
            )
        except Exception:
            logging.exception("ETL task failed during %s", context.stage)
            raise


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

    context = TASK_RUN_CONTEXT.pop(sender.request.id, None)

    try:
        task_run = TaskRun.objects.get(id=sender.request.id)
    except TaskRun.DoesNotExist:
        return

    if not isinstance(result, dict):
        result = {"message": str(result)}

    result = _merge_result_with_context(result, context)
    if context and context.stage and "stage" not in result:
        result["stage"] = context.stage

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

    context = TASK_RUN_CONTEXT.pop(task_id, None)

    try:
        task_run = TaskRun.objects.get(id=task_id)
    except TaskRun.DoesNotExist:
        return

    stage = context.stage if context else None
    message = (
        f"Failed during {stage}: {exception}" if stage else f"{exception}"
    )

    task_run.status = "FAILURE"
    task_run.finished_at = timezone.now()
    task_run.result = _build_task_result(
        message,
        context,
        stage=stage,
        error=str(exception),
        traceback=einfo.traceback,
    )

    task_run.save(update_fields=["status", "finished_at", "result"])


@shared_task(bind=True, expires=10, name="etl.tasks.cleanup_etl_task_runs")
def cleanup_etl_task_runs(self, days=14):
    """
    Celery task to run the cleanup_etl_task_runs management command.
    """

    call_command("cleanup_etl_task_runs", f"--days={days}")
