from __future__ import annotations

import re
from typing import Any, Optional

from .etl_errors import user_facing_error_from_exception


_SUCCESS_LOAD_RE = re.compile(
    r"^Load complete\.\s*(\d+)\s+rows were added to\s+(\d+)\s+datastreams?\.$"
)
_SUCCESS_LOADED_RE = re.compile(
    r"^Loaded\s+(\d+)\s+total observations\s+(?:into|across)\s+(\d+)\s+datastream(?:s|\(s\))\.$"
)
_FAILURE_STAGE_PREFIX_RE = re.compile(
    r"^(?:Setup failed|Failed during [^:]+):\s*",
    re.IGNORECASE,
)


def task_transformer_raw(task: Any) -> Optional[dict[str, Any]]:
    if task is None:
        return None

    data_connection = getattr(task, "data_connection", None)
    if data_connection is None:
        return None

    raw_settings = getattr(data_connection, "transformer_settings", None) or {}
    if not isinstance(raw_settings, dict):
        return None

    raw: dict[str, Any] = dict(raw_settings)
    transformer_type = getattr(data_connection, "transformer_type", None)
    if transformer_type and "type" not in raw:
        raw["type"] = transformer_type
    return raw


def _format_loaded_success_message(loaded: int, ds_count: int) -> str:
    preposition = "into" if ds_count == 1 else "across"
    ds_word = "datastream" if ds_count == 1 else "datastreams"
    return f"Loaded {loaded} total observations {preposition} {ds_count} {ds_word}."


def _extract_message(result: dict[str, Any]) -> Optional[str]:
    for key in ("message", "summary", "error", "detail"):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _normalize_success_message(message: str) -> str:
    m = _SUCCESS_LOAD_RE.match(message)
    if m:
        return _format_loaded_success_message(int(m.group(1)), int(m.group(2)))

    m = _SUCCESS_LOADED_RE.match(message)
    if m:
        return _format_loaded_success_message(int(m.group(1)), int(m.group(2)))

    if (
        message
        == "Already up to date. No new observations were loaded because all timestamps in the source are older than what is already stored."
    ):
        return "Already up to date. No new observations were loaded."

    return message


def _normalize_failure_message(
    message: str,
    *,
    transformer_raw: Optional[dict[str, Any]] = None,
) -> str:
    candidate = _FAILURE_STAGE_PREFIX_RE.sub("", message).strip()

    if candidate.startswith("Error reading CSV data:"):
        candidate = candidate.split("Error reading CSV data:", 1)[1].strip()

    mapped = user_facing_error_from_exception(
        ValueError(candidate),
        transformer_raw=transformer_raw,
    )
    if mapped:
        return str(mapped)
    return candidate or message


def normalize_task_run_result(
    *,
    status: str,
    result: Any,
    transformer_raw: Optional[dict[str, Any]] = None,
) -> Any:
    if result is None:
        return None

    normalized: dict[str, Any]
    if isinstance(result, dict):
        normalized = dict(result)
    else:
        normalized = {"message": str(result)}

    message = _extract_message(normalized)
    if not message:
        return normalized

    if status == "SUCCESS":
        normalized_message = _normalize_success_message(message)
    elif status == "FAILURE":
        normalized_message = _normalize_failure_message(
            message,
            transformer_raw=transformer_raw,
        )
    else:
        normalized_message = message

    normalized["message"] = normalized_message
    summary = normalized.get("summary")
    if not isinstance(summary, str) or not summary.strip() or summary.strip() == message:
        normalized["summary"] = normalized_message

    return normalized
