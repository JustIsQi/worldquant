from __future__ import annotations

import json
from typing import Any


def metric(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def extract_checks(source: dict[str, Any]) -> list[dict[str, Any]]:
    checks = (source.get("is") or {}).get("checks") or source.get("checks") or []
    return checks if isinstance(checks, list) else []


def check_lists(checks: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    failed = [str(c.get("name")) for c in checks if c.get("result") == "FAIL"]
    pending = [str(c.get("name")) for c in checks if c.get("result") == "PENDING"]
    return failed, pending


def parse_json_list(raw: str | None) -> list[Any]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def is_submittable(failed: list[str], pending: list[str]) -> bool:
    return not failed and (not pending or pending == ["SELF_CORRELATION"])
