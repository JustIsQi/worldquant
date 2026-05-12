from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AuthConfig:
    env_file: Path = Path(".env")
    auth_method: str = "auto"
    email: str | None = None
    password: str | None = None
    password_file: Path | None = None


@dataclass(slots=True)
class BrainConfig:
    region: str = "USA"
    universe: str = "TOP3000"
    delay: int = 1
    decay: int = 10
    neutralization: str = "SUBINDUSTRY"
    truncation: float = 0.08
    pasteurization: str = "ON"
    nan_handling: str = "ON"
    max_wait_seconds: int = 900
    submit_poll_seconds: int = 120
    submit_poll_interval: float = 10.0


@dataclass(slots=True)
class RunConfig:
    out_dir: Path = Path("runs")
    target_active: int = 1
    target_active_per_week: int = 2
    daily_budget_minutes: int = 90
    workers: int = 1
    max_inflight: int = 1
    auto_submit: bool = True
    skip_before: int = 1
    limit: int = 0


@dataclass(slots=True)
class FamilyConfig:
    name: str
    builder: str = "simple_rank"
    enabled: bool = True
    fields: list[str] = field(default_factory=list)
    mix_with_price: bool = False
    max_candidates: int = 0


def _default_families() -> dict[str, FamilyConfig]:
    return {
        "leverage": FamilyConfig(
            name="leverage",
            builder="simple_rank",
            fields=["liabilities/assets", "debt/assets", "debt_lt/assets"],
            mix_with_price=True,
        ),
        "quality": FamilyConfig(
            name="quality",
            builder="simple_rank",
            fields=["pnl/assets", "pnl/equity", "cashflow/assets", "pnl/revenue"],
            mix_with_price=True,
        ),
        "value": FamilyConfig(
            name="value",
            builder="simple_rank",
            fields=["bookvalue_ps/close", "revenue/cap", "cashflow/cap", "pnl/cap"],
            mix_with_price=True,
        ),
        "reversal_short": FamilyConfig(
            name="reversal_short",
            builder="signal_passthrough",
            fields=["-ts_delta(close,5)", "-returns", "-ts_zscore(returns,5)"],
        ),
        "momentum_medium": FamilyConfig(
            name="momentum_medium",
            builder="signal_passthrough",
            fields=["ts_rank(returns,120)", "ts_delta(close,60)"],
        ),
        "volume_lowvol": FamilyConfig(
            name="volume_lowvol",
            builder="signal_passthrough",
            fields=["-ts_corr(close,volume,20)", "-ts_std_dev(returns,20)"],
        ),
    }


@dataclass(slots=True)
class CandidateConfig:
    manual_globs: list[str] = field(default_factory=lambda: ["candidates/manual/*.txt"])
    template_files: list[str] = field(default_factory=lambda: ["candidates/templates/default_templates.txt"])
    generated_output_name: str = "candidates.txt"
    filter_failed_history: bool = True
    per_family_max: int = 8
    interleave: bool = True
    mix_weights: list[float] = field(default_factory=lambda: [0.7, 0.5])
    price_mix_component: str = "-rank(ts_delta(close,5))"
    families: dict[str, FamilyConfig] = field(default_factory=_default_families)


@dataclass(slots=True)
class StateConfig:
    active_alphas: Path = Path("state/active_alphas.json")
    skip_history: Path = Path("state/skip_history.json")
    data_fields: Path = Path("state/data_fields.json")


@dataclass(slots=True)
class DailyConfig:
    auth: AuthConfig = field(default_factory=AuthConfig)
    brain: BrainConfig = field(default_factory=BrainConfig)
    run: RunConfig = field(default_factory=RunConfig)
    candidates: CandidateConfig = field(default_factory=CandidateConfig)
    state: StateConfig = field(default_factory=StateConfig)


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return {}
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Load the small YAML subset used by configs/daily.yaml.

    Supports nested maps by indentation and inline lists. It intentionally keeps
    the config dependency-free; install PyYAML is not required.
    """

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            raise ValueError(f"Invalid config line in {path}: {raw_line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        value = _parse_scalar(raw_value)
        parent[key] = value
        if isinstance(value, dict):
            stack.append((indent, value))
    return root


def _path(value: Any, default: Path | None = None) -> Path | None:
    if value is None:
        return default
    return Path(str(value))


def _build_families(raw: Any) -> dict[str, FamilyConfig]:
    if not isinstance(raw, dict) or not raw:
        return _default_families()
    families: dict[str, FamilyConfig] = {}
    for name, body in raw.items():
        if not isinstance(body, dict):
            continue
        families[str(name)] = FamilyConfig(
            name=str(name),
            builder=str(body.get("builder", "simple_rank")),
            enabled=bool(body.get("enabled", True)),
            fields=[str(f) for f in body.get("fields", []) if str(f).strip()],
            mix_with_price=bool(body.get("mix_with_price", False)),
            max_candidates=int(body.get("max_candidates", 0) or 0),
        )
    return families or _default_families()


def _legacy_families(candidate_data: dict[str, Any]) -> dict[str, FamilyConfig] | None:
    if "families" in candidate_data:
        return None
    legacy_keys = {"fundamental_fields", "value_fields", "price_components"}
    if not legacy_keys & set(candidate_data.keys()):
        return None
    fundamentals = list(candidate_data.get("fundamental_fields", []) or [])
    values = list(candidate_data.get("value_fields", []) or [])
    prices = list(candidate_data.get("price_components", []) or [])
    families: dict[str, FamilyConfig] = {}
    if fundamentals:
        families["leverage"] = FamilyConfig(
            name="leverage", builder="simple_rank", fields=[str(f) for f in fundamentals], mix_with_price=True
        )
    if values:
        families["value"] = FamilyConfig(
            name="value", builder="simple_rank", fields=[str(f) for f in values], mix_with_price=True
        )
    if prices:
        families["reversal_short"] = FamilyConfig(
            name="reversal_short", builder="signal_passthrough", fields=[str(f) for f in prices]
        )
    return families or None


def _build_candidate_config(candidate_data: dict[str, Any]) -> CandidateConfig:
    families = _legacy_families(candidate_data) or _build_families(candidate_data.get("families"))
    default_weights = [0.7, 0.5]
    return CandidateConfig(
        manual_globs=list(candidate_data.get("manual_globs", ["candidates/manual/*.txt"])),
        template_files=list(
            candidate_data.get("template_files", ["candidates/templates/default_templates.txt"])
        ),
        generated_output_name=str(candidate_data.get("generated_output_name", "candidates.txt")),
        filter_failed_history=bool(candidate_data.get("filter_failed_history", True)),
        per_family_max=int(candidate_data.get("per_family_max", 8) or 8),
        interleave=bool(candidate_data.get("interleave", True)),
        mix_weights=[float(v) for v in candidate_data.get("mix_weights", default_weights)],
        price_mix_component=str(
            candidate_data.get("price_mix_component", "-rank(ts_delta(close,5))")
        ),
        families=families,
    )


def load_config(path: Path) -> DailyConfig:
    data = load_simple_yaml(path) if path.exists() else {}
    auth_data = data.get("auth", {})
    brain_data = data.get("brain", {})
    run_data = data.get("run", {})
    candidate_data = data.get("candidates", {})
    state_data = data.get("state", {})

    auth = AuthConfig(
        env_file=Path(str(auth_data.get("env_file", ".env"))),
        auth_method=str(auth_data.get("auth_method", "auto")),
        email=auth_data.get("email"),
        password=auth_data.get("password"),
        password_file=_path(auth_data.get("password_file")),
    )
    brain = BrainConfig(
        region=str(brain_data.get("region", "USA")),
        universe=str(brain_data.get("universe", "TOP3000")),
        delay=int(brain_data.get("delay", 1)),
        decay=int(brain_data.get("decay", 10)),
        neutralization=str(brain_data.get("neutralization", "SUBINDUSTRY")),
        truncation=float(brain_data.get("truncation", 0.08)),
        pasteurization=str(brain_data.get("pasteurization", "ON")),
        nan_handling=str(brain_data.get("nan_handling", "ON")),
        max_wait_seconds=int(brain_data.get("max_wait_seconds", 900)),
        submit_poll_seconds=int(brain_data.get("submit_poll_seconds", 120)),
        submit_poll_interval=float(brain_data.get("submit_poll_interval", 10.0)),
    )
    run = RunConfig(
        out_dir=Path(str(run_data.get("out_dir", "runs"))),
        target_active=int(run_data.get("target_active", 1)),
        target_active_per_week=int(run_data.get("target_active_per_week", 2)),
        daily_budget_minutes=int(run_data.get("daily_budget_minutes", 90)),
        workers=int(run_data.get("workers", 1)),
        max_inflight=int(run_data.get("max_inflight", 1)),
        auto_submit=bool(run_data.get("auto_submit", True)),
        skip_before=int(run_data.get("skip_before", 1)),
        limit=int(run_data.get("limit", 0)),
    )
    candidates = _build_candidate_config(candidate_data)
    state = StateConfig(
        active_alphas=Path(str(state_data.get("active_alphas", "state/active_alphas.json"))),
        skip_history=Path(str(state_data.get("skip_history", "state/skip_history.json"))),
        data_fields=Path(str(state_data.get("data_fields", "state/data_fields.json"))),
    )
    return DailyConfig(auth=auth, brain=brain, run=run, candidates=candidates, state=state)
