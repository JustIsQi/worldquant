from __future__ import annotations

import csv
import glob
import itertools
import json
import re
from pathlib import Path
from typing import Any, Callable

from .config import CandidateConfig, FamilyConfig
from .io_utils import dedupe, load_expressions


def _normalize(expression: str) -> str:
    return " ".join(expression.split())


_IDENT_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]+")
_RESERVED_TOKENS = {
    "rank", "group_rank", "ts_delta", "ts_zscore", "ts_rank", "ts_corr",
    "ts_std_dev", "ts_mean", "ts_sum", "ts_max", "ts_min", "trade_when",
    "subindustry", "industry", "sector", "market", "country",
}


def _data_tokens(expression: str) -> set[str]:
    tokens = {m.group(0) for m in _IDENT_RE.finditer(expression)}
    return tokens - _RESERVED_TOKENS


def _failed_entries_from_summary(summary_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not summary_path.exists():
        return entries
    with summary_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            expression = row.get("expression")
            if not expression:
                continue
            failed_raw = row.get("failed")
            submit_result = row.get("submit_result")
            checks_raw = row.get("checks")
            fail_reason: str | None = None
            hard_fail = False
            if failed_raw:
                try:
                    parsed = json.loads(failed_raw)
                except json.JSONDecodeError:
                    parsed = []
                if isinstance(parsed, list) and parsed:
                    hard_fail = True
                    fail_reason = str(parsed[0])
                elif parsed:
                    hard_fail = True
            if checks_raw:
                try:
                    checks = json.loads(checks_raw)
                except json.JSONDecodeError:
                    checks = []
                for check in checks:
                    if isinstance(check, dict) and check.get("result") == "FAIL":
                        hard_fail = True
                        if not fail_reason and check.get("name"):
                            fail_reason = str(check["name"])
                        break
            if hard_fail or submit_result in {"SKIPPED_CHECKS", "REJECTED"}:
                entries.append(
                    {
                        "expression": _normalize(expression),
                        "fail_reason": fail_reason or submit_result or "UNKNOWN",
                    }
                )
    return entries


def failed_expressions_from_summary(summary_path: Path) -> set[str]:
    return {entry["expression"] for entry in _failed_entries_from_summary(summary_path)}


def failed_entries_from_summary(
    summary_path: Path,
    *,
    families: dict[str, FamilyConfig] | None = None,
) -> list[dict[str, Any]]:
    entries = _failed_entries_from_summary(summary_path)
    if families:
        for entry in entries:
            entry["family"] = family_of(entry["expression"], families)
    return entries


def _build_simple_rank(family: FamilyConfig) -> list[str]:
    out: list[str] = []
    for f in family.fields:
        out.extend([f, f"rank({f})", f"group_rank({f}, subindustry)"])
    return out


def _build_signal_passthrough(family: FamilyConfig) -> list[str]:
    out: list[str] = []
    for f in family.fields:
        out.append(f)
        out.append(f"rank({f})")
        out.append(f"group_rank({f}, subindustry)")
    return out


FAMILY_BUILDERS: dict[str, Callable[[FamilyConfig], list[str]]] = {
    "simple_rank": _build_simple_rank,
    "signal_passthrough": _build_signal_passthrough,
}


def _price_mixes(
    family_exprs: list[str],
    weights: list[float],
    price_component: str,
) -> list[str]:
    if not weights or not price_component:
        return []
    primary = next((e for e in family_exprs if e.startswith("rank(")), None)
    if primary is None:
        primary = family_exprs[0] if family_exprs else None
    if primary is None:
        return []
    out: list[str] = []
    for w in weights:
        other = round(1.0 - w, 10)
        out.append(f"{w:g}*{primary}+{other:g}*({price_component})")
    return out


def family_of(expression: str, families: dict[str, FamilyConfig]) -> str | None:
    norm = _normalize(expression)
    for name, family in families.items():
        for f in family.fields:
            token = f.strip()
            if token and token in norm:
                return name
    return None


def generate_rule_candidates(
    config: CandidateConfig,
    *,
    available_fields: set[str] | None = None,
) -> list[str]:
    per_family: list[list[str]] = []
    available = available_fields or set()
    for name, family in config.families.items():
        if not family.enabled or not family.fields:
            continue
        builder = FAMILY_BUILDERS.get(family.builder)
        if builder is None:
            print(
                f"[candidates] unknown builder '{family.builder}' for family '{name}', skipping",
                flush=True,
            )
            continue
        exprs = builder(family)
        if available:
            kept: list[str] = []
            for expression in exprs:
                refs = _data_tokens(expression)
                if not refs or refs.issubset(available):
                    kept.append(expression)
                else:
                    missing = sorted(refs - available)
                    print(
                        f"[candidates] drop '{expression}' (family={name}): "
                        f"unknown fields {missing}",
                        flush=True,
                    )
            exprs = kept
        if family.mix_with_price:
            exprs = exprs + _price_mixes(exprs, config.mix_weights, config.price_mix_component)
        cap = family.max_candidates or config.per_family_max
        if cap:
            exprs = exprs[:cap]
        if exprs:
            per_family.append(exprs)
    if not per_family:
        return []
    if config.interleave:
        interleaved: list[str] = []
        for layer in itertools.zip_longest(*per_family):
            for expression in layer:
                if expression is not None:
                    interleaved.append(expression)
        return dedupe(interleaved)
    return dedupe([e for fam in per_family for e in fam])


def load_template_candidates(paths: list[str]) -> list[str]:
    expressions: list[str] = []
    for pattern in paths:
        for match in sorted(glob.glob(pattern)):
            expressions.extend(load_expressions(Path(match)))
    return expressions


def load_manual_candidates(patterns: list[str]) -> list[str]:
    expressions: list[str] = []
    for pattern in patterns:
        for match in sorted(glob.glob(pattern)):
            expressions.extend(load_expressions(Path(match)))
    return expressions


def failed_history_expressions(runs_dir: Path) -> set[str]:
    failed: set[str] = set()
    for path in runs_dir.glob("**/*.csv"):
        if path.name not in {"summary.csv", "submit_summary.csv"}:
            continue
        failed.update(failed_expressions_from_summary(path))
    return failed


def build_candidate_pool(
    config: CandidateConfig,
    *,
    runs_dir: Path = Path("runs"),
    skip_expressions: set[str] | None = None,
    available_fields: set[str] | None = None,
) -> list[str]:
    manual = load_manual_candidates(config.manual_globs)
    templates = load_template_candidates(config.template_files)
    generated = generate_rule_candidates(config, available_fields=available_fields)
    expressions = dedupe([*manual, *templates, *generated])
    if not config.filter_failed_history and not skip_expressions:
        return expressions
    skip = set(skip_expressions or set())
    if config.filter_failed_history and not skip_expressions:
        skip.update(failed_history_expressions(runs_dir))
    return [expr for expr in expressions if _normalize(expr) not in skip]


def write_candidates(path: Path, expressions: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Generated daily candidate pool.", "# One FASTEXPR alpha per line.", *expressions]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
