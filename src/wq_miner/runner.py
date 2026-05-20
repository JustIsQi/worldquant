from __future__ import annotations

import argparse
import json
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from . import brain
from .checks import check_lists, extract_checks, is_submittable, metric, parse_json_list
from .config import BrainConfig, DailyConfig
from .io_utils import append_csv, utc_stamp
from .state import update_active_alpha


FIELDNAMES = [
    "time_utc",
    "source_index",
    "expression",
    "sim_status",
    "alpha_id",
    "alpha_status",
    "sharpe",
    "fitness",
    "returns",
    "turnover",
    "margin",
    "submit_http_status",
    "submit_check_http_status",
    "submit_result",
    "failed",
    "pending",
    "note",
]


def brain_args(config: BrainConfig, auth_args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        auth_method=auth_args.auth_method,
        email=auth_args.email,
        password=auth_args.password,
        password_file=auth_args.password_file,
        no_password_prompt=True,
        region=config.region,
        universe=config.universe,
        delay=config.delay,
        decay=config.decay,
        neutralization=config.neutralization,
        truncation=config.truncation,
        pasteurization=config.pasteurization,
        nan_handling=config.nan_handling,
        max_wait_seconds=config.max_wait_seconds,
        submit_poll_seconds=config.submit_poll_seconds,
        submit_poll_interval=config.submit_poll_interval,
    )


def metric_row(
    *,
    index: int,
    expression: str,
    result: dict[str, Any],
    alpha: dict[str, Any] | None,
) -> dict[str, Any]:
    source = alpha or result
    isv = source.get("is") or {}
    alpha_id = brain.alpha_id_from_result(result)
    failed, pending = check_lists(extract_checks(source) or result.get("checks") or [])
    return {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "source_index": index,
        "expression": expression,
        "sim_status": result.get("status") or ("COMPLETE" if alpha_id else "UNKNOWN"),
        "alpha_id": alpha_id,
        "alpha_status": source.get("status"),
        "sharpe": isv.get("sharpe"),
        "fitness": isv.get("fitness"),
        "returns": isv.get("returns"),
        "turnover": isv.get("turnover"),
        "margin": isv.get("margin"),
        "failed": json.dumps(failed, ensure_ascii=False),
        "pending": json.dumps(pending, ensure_ascii=False),
    }


class CsvWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = threading.Lock()

    def append(self, row: dict[str, Any]) -> None:
        with self.lock:
            append_csv(self.path, row, FIELDNAMES)


def submit_and_check(
    session,
    alpha_id: str,
    *,
    poll_seconds: int,
    poll_interval: float,
) -> tuple[int, int | None, dict[str, Any] | str, dict[str, Any] | None]:
    response = brain.request_with_backoff(session, "POST", f"{brain.API_BASE}/alphas/{alpha_id}/submit")
    try:
        body: dict[str, Any] | str = response.json()
    except Exception:
        body = response.text[:1000]

    deadline = time.monotonic() + poll_seconds
    last_status: int | None = None
    last_body: dict[str, Any] | str = body
    last_alpha: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        status_response = brain.request_with_backoff(
            session, "GET", f"{brain.API_BASE}/alphas/{alpha_id}/submit"
        )
        last_status = status_response.status_code
        try:
            last_body = status_response.json()
        except Exception:
            last_body = status_response.text[:1000]
        if last_status in {200, 403}:
            last_alpha = brain.fetch_alpha(session, alpha_id)
            break
    if last_alpha is None:
        last_alpha = brain.fetch_alpha(session, alpha_id)
    return response.status_code, last_status, last_body, last_alpha


_thread_local = threading.local()


def _get_thread_session(args: argparse.Namespace):
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = brain.make_session(args)
        _thread_local.session = session
    return session


def process_candidate(
    index: int,
    expression: str,
    *,
    args: argparse.Namespace,
    run_dir: Path,
    auto_submit: bool,
) -> dict[str, Any]:
    session = _get_thread_session(args)
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    response = brain.request_with_backoff(
        session,
        "POST",
        f"{brain.API_BASE}/simulations",
        json=brain.simulation_payload(expression, args),
    )
    location = response.headers.get("Location")
    if response.status_code != 201 or not location:
        return {
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "source_index": index,
            "expression": expression,
            "sim_status": f"SUBMIT_HTTP_{response.status_code}",
            "submit_result": "SIMULATION_SUBMIT_FAILED",
            "note": response.text[:800],
        }

    sim_id = location.rstrip("/").split("/")[-1]
    result = brain.poll_simulation(session, location, max_wait_seconds=args.max_wait_seconds)
    (raw_dir / f"{index:03d}_{sim_id}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    alpha_id = brain.alpha_id_from_result(result)
    alpha = brain.fetch_alpha(session, alpha_id) if alpha_id else None
    if alpha:
        (raw_dir / f"{index:03d}_{alpha_id}_alpha.json").write_text(
            json.dumps(alpha, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    row = metric_row(index=index, expression=expression, result=result, alpha=alpha)
    failed = parse_json_list(str(row.get("failed") or "[]"))
    pending = parse_json_list(str(row.get("pending") or "[]"))
    if not is_submittable([str(v) for v in failed], [str(v) for v in pending]):
        row["submit_result"] = "SKIPPED_CHECKS"
        return row
    if not alpha_id:
        row["submit_result"] = "SKIPPED_NO_ALPHA"
        return row
    if not auto_submit:
        row["submit_result"] = "READY_TO_SUBMIT"
        return row

    if alpha and alpha.get("status") == "ACTIVE":
        row["submit_result"] = "ALREADY_ACTIVE"
        row["alpha_status"] = "ACTIVE"
        row["note"] = (
            "Alpha already ACTIVE in account before this run; no new submission attempted."
        )
        return row

    submit_http, check_http, submit_body, final_alpha = submit_and_check(
        session,
        alpha_id,
        poll_seconds=args.submit_poll_seconds,
        poll_interval=args.submit_poll_interval,
    )
    final_checks = []
    if isinstance(submit_body, dict):
        final_checks = (submit_body.get("is") or {}).get("checks") or []
    if not final_checks and final_alpha:
        final_checks = extract_checks(final_alpha)
    final_failed, final_pending = check_lists(final_checks)
    final_status = (final_alpha or {}).get("status")

    row.update(
        {
            "submit_http_status": submit_http,
            "submit_check_http_status": check_http,
            "alpha_status": final_status,
            "failed": json.dumps(final_failed, ensure_ascii=False),
            "pending": json.dumps(final_pending, ensure_ascii=False),
        }
    )
    if final_status == "ACTIVE":
        row["submit_result"] = "ACTIVE"
    elif check_http == 403:
        row["submit_result"] = "REJECTED"
        note = (
            (submit_body.get("is") or {}).get("selfCorrelated", {})
            if isinstance(submit_body, dict)
            else submit_body
        )
        row["note"] = json.dumps(note, ensure_ascii=False)[:1000]
    else:
        row["submit_result"] = f"UNRESOLVED_{check_http}"
        row["note"] = (
            json.dumps(submit_body, ensure_ascii=False)[:1000]
            if isinstance(submit_body, (dict, list))
            else str(submit_body)[:1000]
        )
    return row


def make_run_dir(config: DailyConfig, run_date: date | None = None) -> Path:
    day = (run_date or date.today()).isoformat()
    return config.run.out_dir / day / f"{utc_stamp()}_daily"


def run_candidates(
    *,
    config: DailyConfig,
    expressions: list[str],
    already_active: set[str],
    auth_args: argparse.Namespace,
    run_dir: Path,
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "submit_summary.csv"
    writer = CsvWriter(summary_path)
    args = brain_args(config.brain, auth_args)

    active: set[str] = set()
    candidates = [
        (i, expr)
        for i, expr in enumerate(expressions, start=1)
        if i >= config.run.skip_before
    ]
    if config.run.limit:
        candidates = candidates[: config.run.limit]

    print(f"run_dir={run_dir}", flush=True)
    print(f"already_active_history={sorted(already_active)}", flush=True)
    print(
        f"queued={len(candidates)} workers={config.run.workers} "
        f"max_inflight={config.run.max_inflight} auto_submit={config.run.auto_submit}",
        flush=True,
    )

    next_candidate = 0
    futures = {}
    budget_seconds = max(0, config.run.daily_budget_minutes) * 60
    started_at = time.monotonic()
    budget_hit = False

    def _budget_exhausted() -> bool:
        return bool(budget_seconds) and (time.monotonic() - started_at) > budget_seconds

    with ThreadPoolExecutor(max_workers=config.run.workers) as executor:
        while (
            (next_candidate < len(candidates) or futures)
            and len(active) < config.run.target_active
            and not budget_hit
        ):
            while (
                next_candidate < len(candidates)
                and len(futures) < config.run.max_inflight
                and len(active) < config.run.target_active
                and not _budget_exhausted()
            ):
                index, expression = candidates[next_candidate]
                next_candidate += 1
                print(f"queue [{index}/{len(expressions)}] {expression}", flush=True)
                future = executor.submit(
                    process_candidate,
                    index,
                    expression,
                    args=args,
                    run_dir=run_dir,
                    auto_submit=config.run.auto_submit,
                )
                futures[future] = (index, expression)

            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                index, expression = futures.pop(future)
                try:
                    row = future.result()
                except Exception as exc:
                    row = {
                        "time_utc": datetime.now(timezone.utc).isoformat(),
                        "source_index": index,
                        "expression": expression,
                        "submit_result": "EXCEPTION",
                        "note": repr(exc),
                    }
                writer.append(row)
                result_label = row.get("submit_result")
                if row.get("alpha_id"):
                    if result_label == "ACTIVE":
                        active.add(str(row["alpha_id"]))
                        update_active_alpha(config.state.active_alphas, row)
                    elif result_label == "ALREADY_ACTIVE":
                        update_active_alpha(config.state.active_alphas, row)
                print(
                    "done [{idx}] alpha={alpha} result={result} status={status} "
                    "sharpe={sharpe} fitness={fitness} failed={failed} pending={pending}".format(
                        idx=index,
                        alpha=row.get("alpha_id"),
                        result=row.get("submit_result"),
                        status=row.get("alpha_status"),
                        sharpe=row.get("sharpe"),
                        fitness=row.get("fitness"),
                        failed=row.get("failed"),
                        pending=row.get("pending"),
                    ),
                    flush=True,
                )
            if _budget_exhausted():
                budget_hit = True
                elapsed = int(time.monotonic() - started_at)
                print(
                    f"budget_exhausted elapsed={elapsed}s budget={budget_seconds}s "
                    f"processed={next_candidate}/{len(candidates)}",
                    flush=True,
                )
    print(f"summary={summary_path}", flush=True)
    return summary_path
