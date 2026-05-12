from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Iterable


def utc_stamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


def load_expressions(path: Path) -> list[str]:
    expressions: list[str] = []
    if not path.exists():
        return expressions
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            expressions.append(line)
    return expressions


def dedupe(expressions: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for expression in expressions:
        normalized = " ".join(expression.strip().split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(expression.strip())
    return unique


def append_csv(path: Path, row: dict[str, Any], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    names = fieldnames or list(row.keys())
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key) for key in names})


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
