from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from pydantic import ValidationError


def _jsonish(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        if value == "":
            return '""'
        return repr(value)
    return repr(value)


_EXTRACTOR_ALIAS_MAP: dict[str, str] = {
    "source_uri": "sourceUri",
    "placeholder_variables": "placeholderVariables",
    "run_time_value": "runTimeValue",
}

_TRANSFORMER_ALIAS_MAP: dict[str, str] = {
    "header_row": "headerRow",
    "data_start_row": "dataStartRow",
    "identifier_type": "identifierType",
    "custom_format": "customFormat",
    "timezone_mode": "timezoneMode",
    "run_time_value": "runTimeValue",
    "jmespath": "JMESPath",
    "target_identifier": "targetIdentifier",
    "source_identifier": "sourceIdentifier",
    "data_transformations": "dataTransformations",
    "lookup_table_id": "lookupTableId",
}


def _alias(component: str, field: str) -> str:
    if component == "extractor":
        return _EXTRACTOR_ALIAS_MAP.get(field, field)
    if component == "transformer":
        return _TRANSFORMER_ALIAS_MAP.get(field, field)
    return field


def _format_loc(component: str, loc: Iterable[Any]) -> str:
    loc_list = list(loc)
    if component == "extractor" and loc_list and loc_list[0] in (
        "HTTPExtractor",
        "LocalFileExtractor",
    ):
        loc_list = loc_list[1:]
    if component == "transformer" and loc_list and loc_list[0] in (
        "JSONTransformer",
        "CSVTransformer",
    ):
        loc_list = loc_list[1:]

    parts: list[str] = []
    for item in loc_list:
        if isinstance(item, int):
            if not parts:
                parts.append(f"[{item}]")
            else:
                parts[-1] = f"{parts[-1]}[{item}]"
            continue
        if isinstance(item, str):
            parts.append(_alias(component, item))
            continue
        parts.append(str(item))
    if not parts:
        return component
    return ".".join([component] + parts)


@dataclass
class EtlUserFacingError(Exception):
    """
    Exception intended to be shown to end users (TaskDetails "run message").

    Keep message short and actionable; put extra information in `details` and `hint`.
    """

    message: str
    stage: Optional[str] = None
    code: Optional[str] = None
    hint: Optional[str] = None
    details: Optional[list[dict[str, Any]]] = None
    debug_error: Optional[str] = None

    def __post_init__(self) -> None:
        # Keep Exception.args populated for Celery/logging/serialization interoperability.
        super().__init__(self.message)

    def __str__(self) -> str:  # pragma: no cover
        return self.message

    def as_failure_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.code:
            out["code"] = self.code
        if self.hint:
            out["hint"] = self.hint
        if self.details:
            out["details"] = self.details
        if self.debug_error:
            out["debug_error"] = self.debug_error
        return out


def user_facing_error_from_validation_error(
    component: str,
    exc: ValidationError,
    *,
    raw: Optional[dict[str, Any]] = None,
    stage: str = "setup",
) -> EtlUserFacingError:
    """
    Turn pydantic's ValidationError into a clean message + structured details.
    """
    errs = exc.errors(include_url=False)
    # pydantic unions often emit errors for all union branches; filter to the selected type when possible.
    if raw and component in ("extractor", "transformer"):
        raw_type = raw.get("type")
        type_to_model = {
            "extractor": {"HTTP": "HTTPExtractor", "local": "LocalFileExtractor"},
            "transformer": {"JSON": "JSONTransformer", "CSV": "CSVTransformer"},
        }
        selected_model = type_to_model.get(component, {}).get(raw_type)
        if selected_model:
            errs = [
                e for e in errs if not e.get("loc") or e["loc"][0] == selected_model
            ] or errs
    details: list[dict[str, Any]] = []
    for e in errs:
        loc = e.get("loc") or ()
        msg = e.get("msg") or "Invalid value"
        e_type = e.get("type")
        inp = e.get("input", None)
        if inp is None and e_type == "string_type":
            msg = "Field must be a string, not null"
        elif inp is None and e_type in ("int_type", "float_type", "bool_type"):
            msg = f"Field must be a {e_type.split('_', 1)[0]}, not null"
        details.append(
            {
                "path": _format_loc(component, loc),
                "message": msg,
                "type": e_type,
                "input": inp,
            }
        )

    first = details[0] if details else None
    if first:
        path = first.get("path") or component
        msg = first.get("message") or "Invalid value"
        inp = _jsonish(first.get("input"))
        suffix = ""
        if len(details) > 1:
            suffix = f" (+{len(details) - 1} more issue(s))"
        fix = ""
        if component in ("extractor", "transformer", "loader"):
            fix = f" Update the Data Connection {component} settings."
        message = f"Invalid {component} configuration at {path}: {msg} (got {inp}).{suffix}{fix}"
    else:
        message = f"Invalid {component} configuration."

    hint = None
    # Provide a consistent, user-facing pointer to where to fix config.
    if component in ("extractor", "transformer", "loader"):
        hint = (
            f"Check the Data Connection {component} settings and fix the field(s) listed above."
        )
        if any(d.get("input") is None for d in details):
            hint = (
                hint
                + " One of the required fields is null; double-check your JSON config for missing values or placeholders that were not substituted."
            )

    return EtlUserFacingError(
        message=message,
        stage=stage,
        code=f"invalid_{component}_config",
        hint=hint,
        details=details or None,
        debug_error=str(exc),
    )


_MISSING_PER_TASK_VAR_RE = re.compile(r"Missing per-task variable '([^']+)'")
_MISSING_PLACEHOLDER_VAR_RE = re.compile(r"Missing placeholder variable: (.+)$")
_TIMESTAMP_COL_NOT_FOUND_RE = re.compile(r"Timestamp column '([^']*)' not found in data\\.")
_SOURCE_COL_NOT_FOUND_RE = re.compile(r"Source (?:column|index) '([^']+)' not found")


def user_facing_error_from_exception(
    exc: Exception,
    *,
    stage: Optional[str] = None,
) -> Optional[EtlUserFacingError]:
    """
    Map common hydroserverpy + ETL errors to user-actionable messages.

    Return None when the exception should fall back to default formatting.
    """
    if isinstance(exc, EtlUserFacingError):
        return exc

    if isinstance(exc, ValidationError):
        # Caller should pass component via user_facing_error_from_validation_error.
        return None

    if isinstance(exc, KeyError):
        if exc.args and isinstance(exc.args[0], str):
            msg = exc.args[0]
        else:
            msg = str(exc)
        m = _MISSING_PER_TASK_VAR_RE.search(msg)
        if m:
            name = m.group(1)
            return EtlUserFacingError(
                message=(
                    f"Missing required per-task extractor variable '{name}'. "
                    f"Add it to the task's extractorVariables."
                ),
                stage=stage,
                code="missing_task_variable",
                hint=f"Add '{name}' to the task's extractorVariables so the extractor can build the source URL.",
                details=[{"variable": name, "scope": "task.extractorVariables"}],
                debug_error=msg,
            )
        m = _MISSING_PLACEHOLDER_VAR_RE.search(msg)
        if m:
            name = m.group(1).strip()
            return EtlUserFacingError(
                message=(
                    f"Extractor sourceUri contains placeholder '{name}', but it was not provided. "
                    f"Define it in extractor.placeholderVariables and provide a value in task.extractorVariables if needed."
                ),
                stage=stage,
                code="missing_placeholder_variable",
                hint=(
                    f"Add '{name}' to extractor.placeholderVariables and (if perTask) provide it in task.extractorVariables."
                ),
                details=[{"variable": name, "scope": "extractor.placeholderVariables"}],
                debug_error=msg,
            )

    if isinstance(exc, TypeError) and "JSONTransformer received None" in str(exc):
        return EtlUserFacingError(
            message=(
                "Transformer did not receive any extracted data to parse. "
                "Fix the extractor configuration so it returns a valid JSON payload."
            ),
            stage=stage,
            code="missing_extracted_payload",
            hint="Verify the extractor sourceUri and that the request returned a valid JSON payload.",
            debug_error=str(exc),
        )

    # hydroserverpy TimestampParser (timezoneMode=daylightSavings) calls ZoneInfo(timezone).
    # If timezone is missing, ZoneInfo(None) raises a confusing TypeError. Surface a clear fix.
    msg_str = str(exc)
    if (
        isinstance(exc, TypeError)
        and "expected str, bytes or os.PathLike object, not NoneType" in msg_str
        and stage in ("transform", "extract", "setup", None)
    ):
        return EtlUserFacingError(
            message="Task configuration is missing required daylight savings offset.",
            stage=stage,
            code="missing_daylight_savings_offset",
            hint=(
                "If your timestamp timezoneMode is 'daylightSavings', you must set the "
                "corresponding timestamp.timezone to an IANA time zone like 'America/Denver'."
            ),
            details=[
                {
                    "message": "timezone is required when timezoneMode is 'daylightSavings'.",
                    "path": "transformer.timestamp.timezone",
                }
            ],
            debug_error=msg_str,
        )

    if (
        ("NoneType" in msg_str or "nonetype" in msg_str.lower())
        and "string" in msg_str.lower()
        and "assign" in msg_str.lower()
    ):
        return EtlUserFacingError(
            message=(
                "A required configuration value is null where a string is expected. "
                "Fix the ETL configuration JSON to provide a value for the missing field."
            ),
            stage=stage,
            code="null_value_in_config",
            hint="Look for missing/empty fields in the Data Connection settings (and any variable substitution that produced null).",
            debug_error=msg_str,
        )

    if isinstance(exc, ValueError):
        msg = msg_str
        m = _TIMESTAMP_COL_NOT_FOUND_RE.search(msg)
        if m:
            key = m.group(1)
            return EtlUserFacingError(
                message=(
                    f"Timestamp column '{key}' was not found in the extracted data. "
                    "Fix the transformer timestamp.key (or identifierType/index settings) to match the extracted data."
                ),
                stage=stage,
                code="timestamp_column_missing",
                hint=(
                    "Update the transformer timestamp.key (or identifierType/index settings) to match the extracted data."
                ),
                debug_error=msg,
            )
        if "Source index" in msg and "out of range" in msg:
            return EtlUserFacingError(
                message=msg,
                stage=stage,
                code="source_index_out_of_range",
                hint="Check the task mappings: a sourceIdentifier index is outside the extracted dataset's column range.",
                debug_error=msg,
            )
        if "Source column" in msg and "not found in extracted data" in msg:
            return EtlUserFacingError(
                message=msg,
                stage=stage,
                code="source_column_missing",
                hint="Check the task mappings: a sourceIdentifier does not exist in the extracted dataset columns.",
                debug_error=msg,
            )

    return None
