import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone as dt_timezone
import os
from typing import Any, Optional
from uuid import UUID
import pandas as pd
from celery import shared_task
from pydantic import TypeAdapter, ValidationError
from celery.signals import task_prerun, task_success, task_failure, task_postrun
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.management import call_command
from domains.etl.models import Task, TaskRun
from .loader import HydroServerInternalLoader, LoadSummary
from .etl_errors import (
    EtlUserFacingError,
    user_facing_error_from_exception,
    user_facing_error_from_validation_error,
)
from hydroserverpy.etl.factories import extractor_factory, transformer_factory
from hydroserverpy.etl.etl_configuration import ExtractorConfig, TransformerConfig, SourceTargetMapping, MappingPath


@dataclass
class TaskRunContext:
    stage: str = "setup"
    runtime_source_uri: Optional[str] = None
    log_handler: Optional["TaskLogHandler"] = None
    task_meta: dict[str, Any] = field(default_factory=dict)
    emitted_runtime_vars_log: bool = False
    emitted_task_vars_log: bool = False


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _safe_lower(value: Any) -> str:
    if value is None:
        return ""
    v = _enum_value(value)
    if isinstance(v, str):
        return v.lower()
    return str(v).lower()


def _validate_daylight_savings_timezone(transformer_cfg: Any, *, stage: str) -> None:
    """
    hydroserverpy allows timezoneMode=daylightSavings with timezone unset, which later fails
    with a non-obvious TypeError from zoneinfo. Catch and explain it.
    """
    ts = getattr(transformer_cfg, "timestamp", None)
    if not ts:
        return
    mode = _safe_lower(getattr(ts, "timezone_mode", None))
    if mode != "daylightsavings":
        return
    tz = getattr(ts, "timezone", None)
    if tz is None or (isinstance(tz, str) and not tz.strip()):
        raise EtlUserFacingError(
            message=(
                "Missing required timezone: transformer.timestamp.timezone "
                "(required when transformer.timestamp.timezoneMode is 'daylightSavings')."
            ),
            stage=stage,
            code="missing_daylight_savings_offset",
            hint=(
                "If transformer.timestamp.timezoneMode is 'daylightSavings', you must set "
                "transformer.timestamp.timezone to an IANA time zone like 'America/Denver'. "
                "In exported config JSON this is typically at: "
                "dataConnection.transformer.settings.timestamp.timezone"
            ),
            details=[
                {
                    "path": "transformer.timestamp.timezone",
                    "message": "Required when transformer.timestamp.timezoneMode is 'daylightSavings'.",
                    "input": tz,
                }
            ],
            debug_error="transformer.timestamp.timezone is null/empty while timezoneMode=daylightSavings",
        )


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
        # hydroserverpy extractor logs (v1.7.0+) are very verbose: it logs one line
        # per variable resolution. We collapse that into at most one runtime-vars
        # log and one task-vars log for the whole task run.
        self._pending_runtime_vars: set[str] = set()
        self._pending_task_vars: set[str] = set()
        self._collecting_placeholder_vars: bool = False

    def emit(self, record: logging.LogRecord) -> None:
        if not self.filter(record):
            return

        message = record.getMessage()

        # Condense hydroserverpy extractor variable resolution logs into one line
        # each for runtime vars and task vars.
        if self._capture_placeholder_var_log(message, record):
            return
        self._flush_placeholder_var_summaries_if_needed(message, record)

        timestamp = datetime.fromtimestamp(record.created, tz=dt_timezone.utc).isoformat()
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

    def _append_synthetic_entry(
        self, *, timestamp: str, level: str, message: str, record: logging.LogRecord
    ) -> None:
        # Mirror the structure of "real" log capture entries.
        line = f"{timestamp} {level:<8} {message}"
        self.lines.append(line)
        self.entries.append(
            {
                "timestamp": timestamp,
                "level": level,
                "logger": record.name,
                "message": message,
                "pathname": record.pathname,
                "lineno": record.lineno,
            }
        )

    def _capture_placeholder_var_log(self, message: str, record: logging.LogRecord) -> bool:
        """
        Returns True if this record should be suppressed from captured logs.

        hydroserverpy.etl.extractors.base logs:
        - "Creating runtime variables..."
        - "Resolving runtime var: <name>"
        - "Resolving task var: <name>"
        - "Resolving extractor placeholder variables (<n> configured)."
        - "Resolving per-task var: <name>"
        - "Resolved placeholder '<name>' (...) -> '...'"
        """

        # Suppress extractor placeholder variable resolution chatter entirely.
        # This includes both the verbose per-variable lines and our older synthetic summaries.
        if message.startswith("Resolving extractor placeholder variables"):
            return True
        if message.startswith("Resolving per-task var:"):
            return True
        if message.startswith("Resolved placeholder"):
            return True

        # If we see a new "creating" marker while already collecting, treat it as a
        # boundary and flush pending summaries first.
        if message == "Creating runtime variables...":
            self._flush_placeholder_var_summaries(record)
            self._collecting_placeholder_vars = True
            return True

        runtime_prefix = "Resolving runtime var:"
        if message.startswith(runtime_prefix):
            name = message.split(runtime_prefix, 1)[1].strip()
            if not self.context.emitted_runtime_vars_log and name:
                self._pending_runtime_vars.add(name)
            self._collecting_placeholder_vars = True
            return True

        task_prefix = "Resolving task var:"
        if message.startswith(task_prefix):
            name = message.split(task_prefix, 1)[1].strip()
            if not self.context.emitted_task_vars_log and name:
                self._pending_task_vars.add(name)
            self._collecting_placeholder_vars = True
            return True

        return False

    def _flush_placeholder_var_summaries_if_needed(
        self, message: str, record: logging.LogRecord
    ) -> None:
        if not self._collecting_placeholder_vars:
            return

        # As soon as we leave the "variable resolution" block, emit summaries.
        if (
            message != "Creating runtime variables..."
            and not message.startswith("Resolving runtime var:")
            and not message.startswith("Resolving task var:")
        ):
            self._flush_placeholder_var_summaries(record)

    def _flush_placeholder_var_summaries(self, record: logging.LogRecord) -> None:
        # Previously we emitted synthetic summary lines like:
        # "Runtime variables (1): start_time"
        # Those are now removed to keep run logs focused.
        self._pending_runtime_vars.clear()
        self._pending_task_vars.clear()
        self._collecting_placeholder_vars = False

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
    info: dict[str, Any] = {"type": type(data).__name__}
    if isinstance(data, (bytes, bytearray)):
        info["bytes"] = len(data)
        return info
    # BytesIO and similar
    try:
        buf = getattr(data, "getbuffer", None)
        if callable(buf):
            info["bytes"] = len(data.getbuffer())
            return info
    except Exception:
        pass
    # Real file handles
    try:
        fileno = getattr(data, "fileno", None)
        if callable(fileno):
            info["bytes"] = os.fstat(data.fileno()).st_size
            return info
    except Exception:
        pass
    return info


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


def _success_message(load: Optional[LoadSummary]) -> str:
    if not load:
        return "Load completed successfully."

    loaded = load.observations_loaded
    if loaded == 0:
        if load.timestamps_total and load.timestamps_after_cutoff == 0:
            if load.cutoff:
                return (
                    "No new observations to load "
                    f"(all timestamps were at or before {load.cutoff})."
                )
            return "No new observations to load (all timestamps were at or before the cutoff)."
        if load.observations_available == 0:
            return "No new observations to load."
        return "No new observations were loaded."

    if load.datastreams_loaded:
        return (
            f"Load completed successfully ({loaded} rows across {load.datastreams_loaded} datastreams)."
        )
    return f"Load completed successfully ({loaded} rows loaded)."


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

    _apply_log_aliases(result)
    return result


def _build_task_result(
    message: str,
    context: Optional[TaskRunContext] = None,
    *,
    stage: Optional[str] = None,
    error: Optional[str] = None,
    traceback: Optional[str] = None,
    code: Optional[str] = None,
    hint: Optional[str] = None,
    details: Optional[list[dict[str, Any]]] = None,
    debug_error: Optional[str] = None,
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
    if code or hint or details or debug_error:
        failure: dict[str, Any] = {}
        if code:
            failure["code"] = code
        if hint:
            failure["hint"] = hint
        if details:
            failure["details"] = details
        if debug_error:
            failure["debug_error"] = debug_error
        result["failure"] = failure

    if context and context.runtime_source_uri:
        _apply_runtime_uri_aliases(result, context.runtime_source_uri)

    if context and context.task_meta and "task" not in result:
        result["task"] = context.task_meta

    if context and context.log_handler:
        logs_text = context.log_handler.as_text()
        if logs_text:
            result["logs"] = logs_text
        if context.log_handler.entries:
            result["log_entries"] = context.log_handler.entries

    _apply_log_aliases(result)
    return result


def _last_logged_error(context: Optional[TaskRunContext]) -> Optional[str]:
    if not context or not context.log_handler or not context.log_handler.entries:
        return None
    for entry in reversed(context.log_handler.entries):
        if entry.get("level") == "ERROR":
            msg = entry.get("message")
            if msg:
                return msg
    return None


def _validate_component_config(component: str, adapter: TypeAdapter, raw: dict[str, Any], *, stage: str):
    try:
        return adapter.validate_python(raw)
    except ValidationError as ve:
        raise user_facing_error_from_validation_error(component, ve, raw=raw, stage=stage) from ve


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

            context.task_meta = {
                "id": str(task.id),
                "name": task.name,
                "data_connection_id": str(task.data_connection_id),
                "data_connection_name": task.data_connection.name,
            }

            context.stage = "setup"
            extractor_raw = {
                "type": task.data_connection.extractor_type,
                **(task.data_connection.extractor_settings or {}),
            }
            transformer_raw = {
                "type": task.data_connection.transformer_type,
                **(task.data_connection.transformer_settings or {}),
            }

            extractor_cfg = _validate_component_config(
                "extractor", TypeAdapter(ExtractorConfig), extractor_raw, stage=context.stage
            )
            transformer_cfg = _validate_component_config(
                "transformer", TypeAdapter(TransformerConfig), transformer_raw, stage=context.stage
            )

            extractor_cls = extractor_factory(extractor_cfg)
            transformer_cls = transformer_factory(transformer_cfg)
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
            extract_summary = _describe_payload(data)
            logging.info("Extractor returned payload: %s", extract_summary)
            if _is_empty(data):
                return _build_task_result(
                    "No data returned from the extractor. Nothing to load.",
                    context,
                    stage=context.stage,
                )

            context.stage = "transform"
            logging.info("Starting transform")
            _validate_daylight_savings_timezone(transformer_cfg, stage=context.stage)
            data = transformer_cls.transform(data, task_mappings)
            transform_summary = _describe_transformed_data(data)
            logging.info("Transform result: %s", transform_summary)
            if _is_empty(data):
                # hydroserverpy's CSVTransformer returns None on read errors (but logs ERROR).
                # Treat that as a failure to avoid misleading "produced no rows" messaging.
                last_err = _last_logged_error(context)
                if last_err and last_err.startswith("Error reading CSV data:"):
                    raise EtlUserFacingError(
                        message=(
                            f"{last_err}. Check delimiter/headerRow/dataStartRow/identifierType "
                            "and confirm the upstream CSV columns match your task mappings."
                        ),
                        stage=context.stage,
                        code="transform_read_error",
                        hint="Fix the CSV transformer settings (delimiter/headerRow/dataStartRow/identifierType) or the upstream CSV format.",
                        debug_error=last_err,
                    )
                return _build_task_result(
                    "Transform produced no rows. Nothing to load.",
                    context,
                    stage=context.stage,
                )

            context.stage = "load"
            logging.info("Starting load")
            load_summary = loader_cls.load(data, task)
            logging.info(
                "Load result: loaded=%s available=%s cutoff=%s",
                getattr(load_summary, "observations_loaded", None),
                getattr(load_summary, "observations_available", None),
                getattr(load_summary, "cutoff", None),
            )

            return _build_task_result(
                _success_message(load_summary),
                context,
                stage=context.stage,
            )
        except Exception as e:
            mapped = user_facing_error_from_exception(e, stage=getattr(context, "stage", None))
            if mapped:
                logging.error("%s", mapped.message)
                if mapped is e:
                    raise
                raise mapped from e
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
    mapped = user_facing_error_from_exception(exception, stage=stage)
    if mapped:
        message = mapped.message
        if stage and message:
            prefix = f"failed during {stage.lower()}:"
            if not message.lower().startswith(prefix):
                message = f"Failed during {stage}: {message}"
        code = mapped.code
        hint = mapped.hint
        details = mapped.details
        debug_error = mapped.debug_error
        error_str = message
    else:
        message = f"Failed during {stage}: {exception}" if stage else f"{exception}"
        code = None
        hint = None
        details = None
        debug_error = None
        error_str = str(exception)

    task_run.status = "FAILURE"
    task_run.finished_at = timezone.now()
    task_run.result = _build_task_result(
        message,
        context,
        stage=stage,
        error=error_str,
        traceback=einfo.traceback,
        code=code,
        hint=hint,
        details=details,
        debug_error=debug_error,
    )

    task_run.save(update_fields=["status", "finished_at", "result"])


@shared_task(bind=True, expires=10, name="etl.tasks.cleanup_etl_task_runs")
def cleanup_etl_task_runs(self, days=14):
    """
    Celery task to run the cleanup_etl_task_runs management command.
    """

    call_command("cleanup_etl_task_runs", f"--days={days}")
