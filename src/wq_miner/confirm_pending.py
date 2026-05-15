from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from . import brain
from .checks import check_lists, extract_checks
from .config import load_config
from .io_utils import append_csv, load_env_file
from .runner import FIELDNAMES
from .state import update_active_alpha


def _summary_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _pending_rows(path: Path) -> list[dict[str, str]]:
    seen: set[str] = set()
    rows: list[dict[str, str]] = []
    for row in _summary_rows(path):
        alpha_id = row.get("alpha_id")
        result = row.get("submit_result") or ""
        if not alpha_id or alpha_id in seen:
            continue
        if result.startswith("UNRESOLVED"):
            seen.add(alpha_id)
            rows.append(row)
    return rows


def _safe_request(session: requests.Session, method: str, url: str, **kwargs: Any) -> requests.Response:
    last: requests.RequestException | None = None
    for attempt in range(1, 7):
        try:
            return brain.request_with_backoff(session, method, url, **kwargs)
        except requests.RequestException as exc:
            last = exc
            sleep = min(60, 5 * attempt)
            print(
                f"network_retry attempt={attempt} sleep={sleep}s "
                f"error={type(exc).__name__}: {exc}",
                flush=True,
            )
            time.sleep(sleep)
    assert last is not None
    raise last


def _fetch_alpha(session: requests.Session, alpha_id: str) -> dict[str, Any] | None:
    response = _safe_request(session, "GET", f"{brain.API_BASE}/alphas/{alpha_id}")
    if response.status_code != 200:
        return None
    return response.json()


def _json_body(response: requests.Response) -> dict[str, Any] | str:
    try:
        return response.json()
    except Exception:
        return response.text[:1000]


def _poll_submit(
    session: requests.Session,
    alpha_id: str,
    *,
    poll_seconds: int,
    poll_interval: float,
) -> tuple[int | None, dict[str, Any] | str, dict[str, Any] | None]:
    deadline = time.monotonic() + poll_seconds
    last_status: int | None = None
    last_body: dict[str, Any] | str = {}
    last_alpha: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        status_response = _safe_request(session, "GET", f"{brain.API_BASE}/alphas/{alpha_id}/submit")
        last_status = status_response.status_code
        last_body = _json_body(status_response)
        last_alpha = _fetch_alpha(session, alpha_id)
        final_status = (last_alpha or {}).get("status")
        checks = (last_body.get("is") or {}).get("checks") if isinstance(last_body, dict) else []
        if not checks and last_alpha:
            checks = extract_checks(last_alpha)
        failed, pending = check_lists(checks or [])
        print(
            f"poll alpha={alpha_id} http={last_status} status={final_status} "
            f"failed={failed} pending={pending}",
            flush=True,
        )
        if final_status == "ACTIVE" or last_status in {403, 404} or failed or not pending:
            break
    if last_alpha is None:
        last_alpha = _fetch_alpha(session, alpha_id)
    return last_status, last_body, last_alpha


def confirm_alpha(
    session: requests.Session,
    row: dict[str, str],
    *,
    poll_seconds: int,
    poll_interval: float,
    resubmit: bool,
) -> dict[str, Any]:
    alpha_id = str(row["alpha_id"])
    submit_status: int | None = None
    submit_body: dict[str, Any] | str = {}
    if resubmit:
        response = _safe_request(session, "POST", f"{brain.API_BASE}/alphas/{alpha_id}/submit")
        submit_status = response.status_code
        submit_body = _json_body(response)
        print(f"resubmit alpha={alpha_id} http={submit_status}", flush=True)

    check_status, check_body, alpha = _poll_submit(
        session,
        alpha_id,
        poll_seconds=poll_seconds,
        poll_interval=poll_interval,
    )
    final_checks = []
    if isinstance(check_body, dict):
        final_checks = (check_body.get("is") or {}).get("checks") or []
    if not final_checks and alpha:
        final_checks = extract_checks(alpha)
    failed, pending = check_lists(final_checks)
    final_status = (alpha or {}).get("status")

    out: dict[str, Any] = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "source_index": row.get("source_index"),
        "expression": row.get("expression"),
        "sim_status": row.get("sim_status"),
        "alpha_id": alpha_id,
        "alpha_status": final_status,
        "sharpe": row.get("sharpe"),
        "fitness": row.get("fitness"),
        "returns": row.get("returns"),
        "turnover": row.get("turnover"),
        "margin": row.get("margin"),
        "submit_http_status": submit_status,
        "submit_check_http_status": check_status,
        "failed": json.dumps(failed, ensure_ascii=False),
        "pending": json.dumps(pending, ensure_ascii=False),
    }
    if final_status == "ACTIVE":
        out["submit_result"] = "ACTIVE"
    elif check_status == 403 or failed:
        out["submit_result"] = "REJECTED"
    else:
        out["submit_result"] = f"UNRESOLVED_{check_status}"
    note_body = check_body if check_body else submit_body
    out["note"] = (
        json.dumps(note_body, ensure_ascii=False)[:1000]
        if isinstance(note_body, (dict, list))
        else str(note_body)[:1000]
    )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/daily.yaml"))
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resubmit", action="store_true")
    parser.add_argument("--no-env-file", action="store_true")
    parser.add_argument("--auth-method", choices=["auto", "password", "cookies"])
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--password-file", type=Path)
    parser.add_argument("--poll-seconds", type=int)
    parser.add_argument("--poll-interval", type=float)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if not args.no_env_file:
        load_env_file(config.auth.env_file)

    auth_args = argparse.Namespace(
        auth_method=args.auth_method or config.auth.auth_method,
        email=args.email or config.auth.email,
        password=args.password or config.auth.password,
        password_file=args.password_file or config.auth.password_file,
        no_password_prompt=True,
    )
    session = brain.make_session(auth_args)
    brain.check_auth(session)

    rows = _pending_rows(args.summary)
    output = args.output or (args.summary.parent / "pending_confirmations.csv")
    print(f"pending={len(rows)} output={output}", flush=True)
    for row in rows:
        confirmed = confirm_alpha(
            session,
            row,
            poll_seconds=args.poll_seconds or config.brain.submit_poll_seconds,
            poll_interval=args.poll_interval or config.brain.submit_poll_interval,
            resubmit=args.resubmit,
        )
        append_csv(output, confirmed, FIELDNAMES)
        if confirmed.get("submit_result") == "ACTIVE":
            update_active_alpha(config.state.active_alphas, confirmed)
        print(
            "confirmed alpha={alpha} result={result} status={status} "
            "failed={failed} pending={pending}".format(
                alpha=confirmed.get("alpha_id"),
                result=confirmed.get("submit_result"),
                status=confirmed.get("alpha_status"),
                failed=confirmed.get("failed"),
                pending=confirmed.get("pending"),
            ),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
