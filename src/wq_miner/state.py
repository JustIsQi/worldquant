from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _normalize(expression: str) -> str:
    return " ".join(expression.split())


def load_active_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"alphas": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"alphas": []}
    if not isinstance(data, dict):
        return {"alphas": []}
    alphas = data.get("alphas")
    if not isinstance(alphas, list):
        data["alphas"] = []
    return data


def active_ids(path: Path) -> set[str]:
    data = load_active_state(path)
    ids: set[str] = set()
    for alpha in data.get("alphas", []):
        if isinstance(alpha, dict) and alpha.get("alpha_id"):
            ids.add(str(alpha["alpha_id"]))
    return ids


def update_active_alpha(path: Path, row: dict[str, Any]) -> None:
    alpha_id = row.get("alpha_id")
    if not alpha_id:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    data = load_active_state(path)
    alphas = [a for a in data.get("alphas", []) if str(a.get("alpha_id")) != str(alpha_id)]
    alphas.append(
        {
            "alpha_id": str(alpha_id),
            "expression": row.get("expression"),
            "status": row.get("alpha_status") or "ACTIVE",
            "sharpe": row.get("sharpe"),
            "fitness": row.get("fitness"),
            "returns": row.get("returns"),
            "turnover": row.get("turnover"),
            "margin": row.get("margin"),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        }
    )
    data["alphas"] = alphas
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def active_expressions(path: Path) -> set[str]:
    data = load_active_state(path)
    expressions: set[str] = set()
    for alpha in data.get("alphas", []):
        if isinstance(alpha, dict) and alpha.get("expression"):
            expressions.add(_normalize(str(alpha["expression"])))
    return expressions


def _coerce_entry(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        expr = _normalize(item)
        if not expr:
            return None
        return {"expression": expr, "family": None, "fail_reason": None}
    if isinstance(item, dict):
        expr = _normalize(str(item.get("expression") or ""))
        if not expr:
            return None
        return {
            "expression": expr,
            "family": item.get("family"),
            "fail_reason": item.get("fail_reason"),
        }
    return None


def load_skip_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, dict):
        return []
    raw = data.get("entries")
    if not isinstance(raw, list):
        legacy = data.get("expressions")
        raw = legacy if isinstance(legacy, list) else []
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        entry = _coerce_entry(item)
        if not entry or entry["expression"] in seen:
            continue
        seen.add(entry["expression"])
        entries.append(entry)
    return entries


def load_skip_history(path: Path) -> set[str]:
    return {entry["expression"] for entry in load_skip_entries(path)}


def save_skip_history(path: Path, items: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    coerced: dict[str, dict[str, Any]] = {}
    for item in items:
        entry = _coerce_entry(item)
        if not entry:
            continue
        coerced[entry["expression"]] = entry
    payload = {
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "entries": sorted(coerced.values(), key=lambda e: e["expression"]),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_skip_expressions(path: Path, new_items: Iterable[Any]) -> list[dict[str, Any]]:
    existing = {entry["expression"]: entry for entry in load_skip_entries(path)}
    for item in new_items:
        entry = _coerce_entry(item)
        if not entry:
            continue
        previous = existing.get(entry["expression"], {})
        existing[entry["expression"]] = {
            "expression": entry["expression"],
            "family": entry.get("family") or previous.get("family"),
            "fail_reason": entry.get("fail_reason") or previous.get("fail_reason"),
        }
    save_skip_history(path, existing.values())
    return list(existing.values())
