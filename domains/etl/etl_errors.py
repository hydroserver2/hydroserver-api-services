from __future__ import annotations

import json
import re
from typing import Any, Iterable, Optional

from pydantic import ValidationError


class EtlUserFacingError(Exception):
    """
    Exception intended to be shown to end users (TaskDetails "run message").

    Keep this as a single readable string. Avoid structured payloads.
    """


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
    # Strip pydantic union branch model names from the front.
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


def _jsonish(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        if value == "":
            return '""'
        return repr(value)
    return repr(value)


def user_facing_error_from_validation_error(
    component: str,
    exc: ValidationError,
    *,
    raw: Optional[dict[str, Any]] = None,
) -> EtlUserFacingError:
    """
    Convert pydantic's ValidationError into one readable, actionable sentence.
    """
    errs = exc.errors(include_url=False)

    # Unions emit errors for every branch. Filter to the selected type when possible.
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

    if not errs:
        return EtlUserFacingError(f"Invalid {component} configuration.")

    first = errs[0]
    loc = first.get("loc") or ()
    msg = first.get("msg") or "Invalid value"
    inp = first.get("input", None)

    path = _format_loc(component, loc)
    message = (
        f"Invalid {component} configuration at {path}: {msg} (got {_jsonish(inp)}). "
        f"Fix: update the Data Connection {component} settings."
    )
    return EtlUserFacingError(message)


_MISSING_PER_TASK_VAR_RE = re.compile(r"Missing per-task variable '([^']+)'")
_MISSING_PLACEHOLDER_VAR_RE = re.compile(r"Missing placeholder variable: (.+)$")
_TIMESTAMP_COL_NOT_FOUND_RE = re.compile(r"Timestamp column '([^']*)' not found in data\.")

_MISSING_REQUIRED_TASK_VAR_RE = re.compile(
    r"Missing required per-task extractor variable '([^']+)'"
)
_MISSING_URI_PLACEHOLDER_RE = re.compile(
    r"Extractor source URI contains a placeholder '([^']+)', but it was not provided"
)
_SOURCE_INDEX_OOR_RE = re.compile(r"Source index (\d+) is out of range for extracted data\.")
_SOURCE_COL_NOT_FOUND_RE = re.compile(
    r"Source column '([^']+)' not found in extracted data\."
)


def user_facing_error_from_exception(
    exc: Exception,
) -> Optional[EtlUserFacingError]:
    """
    Map common ETL/hydroserverpy exceptions to a single readable message.
    """
    if isinstance(exc, EtlUserFacingError):
        return exc

    if isinstance(exc, ValidationError):
        return None

    if isinstance(exc, KeyError):
        msg = exc.args[0] if exc.args and isinstance(exc.args[0], str) else str(exc)
        m = _MISSING_PER_TASK_VAR_RE.search(msg)
        if m:
            name = m.group(1)
            return EtlUserFacingError(
                f"Missing required per-task extractor variable '{name}'. "
                f"Fix: add it to task.extractorVariables."
            )
        m = _MISSING_PLACEHOLDER_VAR_RE.search(msg)
        if m:
            name = m.group(1).strip()
            return EtlUserFacingError(
                f"Extractor sourceUri contains placeholder '{name}', but it was not provided. "
                f"Fix: define it in extractor.placeholderVariables and provide a value in task.extractorVariables if needed."
            )

    msg_str = str(exc)

    if isinstance(exc, TypeError) and "JSONTransformer received None" in msg_str:
        return EtlUserFacingError(
            "Transformer did not receive any extracted data to parse. "
            "Fix: update the extractor configuration so it returns a valid JSON payload."
        )

    if isinstance(exc, TypeError) and "CSVTransformer received None" in msg_str:
        return EtlUserFacingError(
            "Transformer did not receive any extracted data to parse. "
            "Fix: update the extractor configuration so it returns a valid CSV payload."
        )

    if (
        ("NoneType" in msg_str or "nonetype" in msg_str.lower())
        and "string" in msg_str.lower()
        and "assign" in msg_str.lower()
    ):
        return EtlUserFacingError(
            "A required configuration value is null where a string is expected. "
            "Fix: provide the missing value in your ETL configuration JSON."
        )

    # django-ninja HttpError (avoid importing ninja here to keep module import-safe)
    status = getattr(exc, "status_code", None)
    if status is not None and exc.__class__.__name__ == "HttpError":
        message = getattr(exc, "message", None) or msg_str
        if "Datastream does not exist" in message:
            return EtlUserFacingError(
                "The target data series (datastream) could not be found. "
                "Fix: update task mappings so each targetIdentifier is a valid datastream ID."
            )
        if status in (401, 403):
            return EtlUserFacingError(
                "HydroServer rejected the load due to authorization. "
                "Fix: confirm the target datastream(s) belong to this workspace and the job has permission to write."
            )
        if status >= 400:
            return EtlUserFacingError(
                "HydroServer rejected some or all of the data. "
                "Fix: verify the transformed timestamps/values are valid and the target datastream mappings are correct."
            )

    if isinstance(exc, ValueError):
        # Extractor placeholder/variable resolution
        m = _MISSING_REQUIRED_TASK_VAR_RE.search(msg_str)
        if m:
            name = m.group(1)
            return EtlUserFacingError(
                f"Missing required per-task extractor variable '{name}'. "
                "Fix: add it to task.extractorVariables."
            )
        m = _MISSING_URI_PLACEHOLDER_RE.search(msg_str)
        if m:
            name = m.group(1)
            return EtlUserFacingError(
                f"Extractor sourceUri contains placeholder '{name}', but it was not provided. "
                "Fix: define it in extractor.placeholderVariables and provide a value in task.extractorVariables if needed."
            )

        # CSV read errors from hydroserverpy (already user-friendly, but add the one place to fix)
        if msg_str in (
            "The header row contained unexpected values and could not be processed.",
            "One or more data rows contained unexpected values and could not be processed.",
        ):
            return EtlUserFacingError(
                f"{msg_str} Fix: check transformer.delimiter/headerRow/dataStartRow/identifierType "
                "and confirm the upstream CSV columns match your task mappings."
            )

        # JSON transformer common configuration errors
        if msg_str == "The payload's expected fields were not found.":
            return EtlUserFacingError(
                "The payload's expected fields were not found. "
                "Fix: update transformer.JMESPath and transformer.timestamp.key so the extracted JSON produces the expected fields."
            )
        if msg_str == "The timestamp or value key could not be found with the specified query.":
            return EtlUserFacingError(
                "The timestamp or value key could not be found with the specified query. "
                "Fix: update transformer.JMESPath and/or transformer.timestamp.key to match the extracted JSON."
            )

        m = _TIMESTAMP_COL_NOT_FOUND_RE.search(msg_str)
        if m:
            key = m.group(1)
            return EtlUserFacingError(
                f"Timestamp column '{key}' was not found in the extracted data. "
                "Fix: update transformer.timestamp.key (or identifierType/index settings) to match the extracted data."
            )

        m = _SOURCE_INDEX_OOR_RE.search(msg_str)
        if m:
            idx = m.group(1)
            return EtlUserFacingError(
                f"A mapping source index ({idx}) is out of range for the extracted data. "
                "Fix: update task.mappings sourceIdentifier values (or switch identifierType) to match the extracted columns."
            )

        m = _SOURCE_COL_NOT_FOUND_RE.search(msg_str)
        if m:
            col = m.group(1)
            return EtlUserFacingError(
                f"A mapping source column '{col}' was not found in the extracted data. "
                "Fix: update task.mappings sourceIdentifier values to match the extracted columns."
            )

        # JSON decode failures (usually extractor returned HTML/text instead of JSON)
        if isinstance(exc, json.JSONDecodeError):
            return EtlUserFacingError(
                "Extractor returned invalid JSON. "
                "Fix: verify the extractor sourceUri returns JSON (and adjust transformer.JMESPath if needed)."
            )

    return None
