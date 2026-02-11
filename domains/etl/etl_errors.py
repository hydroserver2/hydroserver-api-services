from __future__ import annotations

import ast
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
    if (
        component == "extractor"
        and loc_list
        and loc_list[0]
        in (
            "HTTPExtractor",
            "LocalFileExtractor",
        )
    ):
        loc_list = loc_list[1:]
    if (
        component == "transformer"
        and loc_list
        and loc_list[0]
        in (
            "JSONTransformer",
            "CSVTransformer",
        )
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
    if component == "transformer" and isinstance(raw, dict):
        ts = raw.get("timestamp")
        if isinstance(ts, dict):
            tz_mode = ts.get("timezoneMode") or ts.get("timezone_mode")
            tz_val = ts.get("timezone")
            if (
                path.endswith("transformer.timestamp.timezone")
                and str(tz_mode) == "daylightSavings"
            ):
                if tz_val is None or str(tz_val).strip() == "":
                    return EtlUserFacingError(
                        "Timezone information is required when daylight savings mode is enabled. "
                        "Select a valid timezone such as America/Denver and try again."
                    )
                if "Invalid timezone" in str(msg):
                    return EtlUserFacingError(
                        "The configured timezone is not recognized. "
                        "Use a valid IANA timezone such as America/Denver and run the job again."
                    )

    message = (
        f"Invalid {component} configuration at {path}: {msg} (got {_jsonish(inp)}). "
        f"Update the Data Connection {component} settings."
    )
    return EtlUserFacingError(message)


_MISSING_PER_TASK_VAR_RE = re.compile(r"Missing per-task variable '([^']+)'")
_MISSING_PLACEHOLDER_VAR_RE = re.compile(r"Missing placeholder variable: (.+)$")
_TIMESTAMP_COL_NOT_FOUND_RE = re.compile(
    r"Timestamp column '([^']*)' not found in data\."
)

_MISSING_REQUIRED_TASK_VAR_RE = re.compile(
    r"Missing required per-task extractor variable '([^']+)'"
)
_MISSING_URI_PLACEHOLDER_RE = re.compile(
    r"Extractor source URI contains a placeholder '([^']+)', but it was not provided"
)
_SOURCE_INDEX_OOR_RE = re.compile(
    r"Source index (\d+) is out of range for extracted data\."
)
_SOURCE_COL_NOT_FOUND_RE = re.compile(
    r"Source column '([^']+)' not found in extracted data\."
)
_USECOLS_NOT_FOUND_RE = re.compile(
    r"columns expected but not found:\s*(\[[^\]]*\])",
    re.IGNORECASE,
)


def _iter_exception_chain(exc: Exception) -> Iterable[Exception]:
    seen: set[int] = set()
    current: Optional[Exception] = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        next_exc = current.__cause__ or current.__context__
        current = next_exc if isinstance(next_exc, Exception) else None


def _extract_missing_usecols(exc: Exception) -> list[str]:
    for err in _iter_exception_chain(exc):
        msg = str(err)
        match = _USECOLS_NOT_FOUND_RE.search(msg)
        if not match:
            continue

        raw_list = match.group(1)
        try:
            parsed = ast.literal_eval(raw_list)
            if isinstance(parsed, (list, tuple, set)):
                cols = [str(c).strip() for c in parsed if str(c).strip()]
                if cols:
                    return cols
        except Exception:
            pass

        inner = raw_list.strip()[1:-1]
        if inner:
            cols = [part.strip().strip("'\"") for part in inner.split(",")]
            cols = [c for c in cols if c]
            if cols:
                return cols
    return []


def _format_cols(cols: list[str], max_cols: int = 4) -> str:
    shown = [f"'{c}'" for c in cols[:max_cols]]
    if len(cols) > max_cols:
        shown.append(f"+{len(cols) - max_cols} more")
    return ", ".join(shown)


def user_facing_error_from_exception(
    exc: Exception,
    *,
    transformer_raw: Optional[dict[str, Any]] = None,
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
                f"A required task variable named '{name}' was not provided. "
                "Add a value for it in the task configuration and run the job again."
            )
        m = _MISSING_PLACEHOLDER_VAR_RE.search(msg)
        if m:
            name = m.group(1).strip()
            return EtlUserFacingError(
                f"The extractor URL includes a placeholder '{name}', but no value was supplied. "
                "Provide the missing value in the task variables."
            )

    msg_str = str(exc)

    if isinstance(exc, TypeError) and "JSONTransformer received None" in msg_str:
        return EtlUserFacingError(
            "The transformer did not receive any extracted data to parse. "
            "Confirm the extractor is returning a valid JSON payload."
        )

    if isinstance(exc, TypeError) and "CSVTransformer received None" in msg_str:
        return EtlUserFacingError(
            "The transformer did not receive any extracted data to parse. "
            "Confirm the extractor is returning a valid CSV payload."
        )

    if (
        ("NoneType" in msg_str or "nonetype" in msg_str.lower())
        and "string" in msg_str.lower()
        and "assign" in msg_str.lower()
    ):
        return EtlUserFacingError(
            "A required configuration value is null where a string is expected. "
            "Provide the missing value in your ETL configuration JSON."
        )

    # django-ninja HttpError (avoid importing ninja here to keep module import-safe)
    status = getattr(exc, "status_code", None)
    if status is not None and exc.__class__.__name__ == "HttpError":
        message = getattr(exc, "message", None) or msg_str
        if "Datastream does not exist" in message:
            return EtlUserFacingError(
                "One or more destination datastream identifiers could not be found in HydroServer. "
                "Update the task mappings to use valid datastream IDs."
            )
        if status in (401, 403):
            return EtlUserFacingError(
                "HydroServer rejected the load due to authorization. "
                "Confirm the target datastream(s) belong to this workspace and the job has permission to write."
            )
        if status >= 400:
            return EtlUserFacingError(
                "HydroServer rejected some or all of the data. "
                "Verify the transformed timestamps/values are valid and the target datastream mappings are correct."
            )

    if isinstance(exc, ValueError):
        # Extractor placeholder/variable resolution
        m = _MISSING_REQUIRED_TASK_VAR_RE.search(msg_str)
        if m:
            name = m.group(1)
            return EtlUserFacingError(
                f"A required task variable named '{name}' was not provided. "
                "Add a value for it in the task configuration and run the job again."
            )
        m = _MISSING_URI_PLACEHOLDER_RE.search(msg_str)
        if m:
            name = m.group(1)
            return EtlUserFacingError(
                f"The extractor URL includes a placeholder '{name}', but no value was supplied. "
                "Provide the missing value in the task variables."
            )

        if "identifierType='index' requires timestamp.key" in msg_str:
            return EtlUserFacingError(
                "The timestamp column is set incorrectly. Index mode expects a 1-based column number (1 for the first column). "
                "Update the timestamp setting to a valid column index."
            )

        if msg_str.startswith(
            "One or more timestamps could not be read with the current settings"
        ):
            return EtlUserFacingError(
                "One or more timestamps could not be read using the current format and timezone settings. "
                "Confirm how dates appear in the source file and update the transformer configuration to match."
            )

        if (
            msg_str
            == "One or more configured CSV columns were not found in the header row."
        ):
            missing_cols = _extract_missing_usecols(exc)
            if len(missing_cols) > 1:
                return EtlUserFacingError(
                    f"Configured CSV columns were not found in the file header ({_format_cols(missing_cols)}). "
                    "This often means the delimiter or headerRow setting is incorrect. "
                    "Verify the delimiter and headerRow settings, then run the job again."
                )
            if len(missing_cols) == 1 and isinstance(transformer_raw, dict):
                ts_cfg = transformer_raw.get("timestamp")
                ts_key = ts_cfg.get("key") if isinstance(ts_cfg, dict) else None
                if ts_key is not None and str(missing_cols[0]) == str(ts_key):
                    col = missing_cols[0]
                    return EtlUserFacingError(
                        f"The configured timestamp column '{col}' was not found in the file header. "
                        "Confirm the timestamp mapping and verify the delimiter/headerRow settings match the source file."
                    )
            return EtlUserFacingError(
                "A required column was not found in the file header. "
                "The source file may have changed or the header row may be set incorrectly. "
                "Confirm the file layout and update the column mappings if needed."
            )
        if (
            msg_str
            == "The header row contained unexpected values and could not be processed."
        ):
            return EtlUserFacingError(
                "A required column was not found in the file header. "
                "The source file may have changed or the header row may be set incorrectly. "
                "Confirm the file layout and update the column mappings if needed."
            )
        if (
            msg_str
            == "One or more data rows contained unexpected values and could not be processed."
        ):
            return EtlUserFacingError(
                "A required column was not found in the file header. "
                "The source file may have changed or the header row may be set incorrectly. "
                "Confirm the file layout and update the column mappings if needed."
            )

        # JSON transformer common configuration errors
        if msg_str == "The payload's expected fields were not found.":
            return EtlUserFacingError(
                "Failed to find the timestamp or value using the current JSON query. "
                "Confirm the JMESPath expression matches the structure returned by the source."
            )
        if (
            msg_str
            == "The timestamp or value key could not be found with the specified query."
        ):
            return EtlUserFacingError(
                "Failed to find the timestamp or value using the current JSON query. "
                "Confirm the JMESPath expression matches the structure returned by the source."
            )

        m = _TIMESTAMP_COL_NOT_FOUND_RE.search(msg_str)
        if m:
            col = m.group(1)
            return EtlUserFacingError(
                f"The configured timestamp column '{col}' was not found in the file header. "
                "Confirm the timestamp mapping and verify the delimiter/headerRow settings match the source file."
            )

        m = _SOURCE_INDEX_OOR_RE.search(msg_str)
        if m:
            idx = m.group(1)
            return EtlUserFacingError(
                f"A mapping source index ({idx}) is out of range for the extracted data. "
                "Update task.mappings sourceIdentifier values (or switch identifierType) to match the extracted columns."
            )

        m = _SOURCE_COL_NOT_FOUND_RE.search(msg_str)
        if m:
            col = m.group(1)
            return EtlUserFacingError(
                f"A mapped field named '{col}' was not found in the extracted data. "
                "Update the task mapping so the source identifier matches the JSON."
            )

        # JSON decode failures (usually extractor returned HTML/text instead of JSON)
        if isinstance(exc, json.JSONDecodeError):
            return EtlUserFacingError(
                "The source did not return valid JSON. "
                "Verify the URL points to a JSON endpoint."
            )

        if msg_str == "Could not connect to the source system.":
            return EtlUserFacingError(
                "Failed to connect to the source system. This may be temporary; try again shortly. "
                "If it persists, the source system may be offline."
            )

        if msg_str == "The requested data could not be found on the source system.":
            return EtlUserFacingError(
                "The requested data could not be found on the source system. "
                "Verify the URL is correct and that the file or endpoint still exists."
            )

        if msg_str.startswith("Authentication with the source system failed."):
            return EtlUserFacingError(
                "Authentication with the source system failed. The username, password, or token may be incorrect or expired. "
                "Update the credentials and try again."
            )

        if msg_str in (
            "The connection to the source worked but no observations were returned.",
        ):
            return EtlUserFacingError(
                "No observations were returned from the source system. "
                "Confirm the configured source system has observations available for the requested time range."
            )

        # Backward-compatible mappings for older hydroserverpy strings.
        if msg_str == "The requested payload was not found on the source system.":
            return EtlUserFacingError(
                "The requested data could not be found on the source system. "
                "Verify the URL is correct and that the file or endpoint still exists."
            )

        if msg_str == "The source system returned no data.":
            return EtlUserFacingError(
                "No observations were returned from the source system. "
                "Confirm the configured source system has observations available for the requested time range."
            )

        if (
            msg_str
            == "Authentication with the source system failed; credentials may be invalid or expired."
        ):
            return EtlUserFacingError(
                "Authentication with the source system failed. The username, password, or token may be incorrect or expired. "
                "Update the credentials and try again."
            )

    if "jmespath.exceptions" in msg_str or "Parse error at column" in msg_str:
        return EtlUserFacingError(
            "The JSON query used to extract timestamps or values is invalid or returned unexpected data. "
            "Review and correct the JMESPath expression."
        )

    if msg_str in (
        "The target datastream could not be found.",
        "The target data series (datastream) could not be found.",
        "The target datastream was not found.",
    ):
        return EtlUserFacingError(
            "One or more destination datastream identifiers could not be found in HydroServer. "
            "Update the task mappings to use valid datastream IDs."
        )

    return None
