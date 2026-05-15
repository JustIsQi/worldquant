#!/usr/bin/env python3
"""Batch simulate WorldQuant BRAIN FASTEXPR alphas."""

from __future__ import annotations

import argparse
import csv
import getpass
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


API_BASE = "https://api.worldquantbrain.com"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_expressions(path: Path) -> list[str]:
    expressions: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            expressions.append(line)
    return expressions


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


def base_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "worldquant-local-miner/0.1",
        }
    )
    return session


def chrome_cookie_session() -> requests.Session:
    try:
        import browser_cookie3
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: browser-cookie3. Run `python3 -m pip install -r requirements.txt`."
        ) from exc

    session = base_session()
    session.cookies.update(browser_cookie3.chrome(domain_name="worldquantbrain.com"))
    return session


def password_session(email: str, password: str) -> requests.Session:
    session = base_session()
    response = session.post(
        f"{API_BASE}/authentication",
        auth=(email, password),
        timeout=45,
    )
    if response.status_code not in {200, 201}:
        raise SystemExit(
            f"Password authentication failed ({response.status_code}): {response.text[:300]}"
        )
    return session


def load_password(args: argparse.Namespace) -> str | None:
    if args.password:
        return args.password
    if args.password_file:
        return args.password_file.read_text(encoding="utf-8").splitlines()[0].strip()
    return os.getenv("WQB_PASSWORD") or os.getenv("WORLDQUANT_PASSWORD")


def make_session(args: argparse.Namespace) -> requests.Session:
    email = args.email or os.getenv("WQB_EMAIL") or os.getenv("WORLDQUANT_EMAIL")
    password = load_password(args)
    if args.auth_method in {"auto", "password"} and email:
        if password is None and sys.stdin.isatty() and not args.no_password_prompt:
            password = getpass.getpass(f"WorldQuant BRAIN password for {email}: ")
        if password:
            print("auth_method=password", flush=True)
            return password_session(email, password)
        if args.auth_method == "password":
            raise SystemExit(
                "Password authentication requires WQB_EMAIL and WQB_PASSWORD "
                "or --email plus --password-file."
            )

    if args.auth_method in {"auto", "cookies"}:
        print("auth_method=cookies", flush=True)
        return chrome_cookie_session()

    raise SystemExit("No usable authentication method configured.")


def request_with_backoff(
    session: requests.Session,
    method: str,
    url: str,
    *,
    max_attempts: int = 8,
    **kwargs: Any,
) -> requests.Response:
    for attempt in range(1, max_attempts + 1):
        response = session.request(method, url, timeout=45, **kwargs)
        if response.status_code != 429:
            return response
        retry_after = float(response.headers.get("Retry-After") or min(60, 5 * attempt))
        print(f"rate limited; sleeping {retry_after:.1f}s", flush=True)
        time.sleep(retry_after)
    return response


def check_auth(session: requests.Session) -> None:
    response = request_with_backoff(session, "GET", f"{API_BASE}/authentication")
    if response.status_code != 200:
        raise SystemExit(
            f"Authentication check failed ({response.status_code}). Log in again or verify credentials."
        )
    data = response.json()
    user_id = data.get("user", {}).get("id", "unknown")
    permissions = ",".join(data.get("permissions", [])) or "none"
    expiry = data.get("token", {}).get("expiry")
    print(f"authenticated as {user_id}; permissions={permissions}; token_expiry={expiry}", flush=True)


def simulation_payload(expression: str, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": args.region,
            "universe": args.universe,
            "delay": args.delay,
            "decay": args.decay,
            "neutralization": args.neutralization,
            "truncation": args.truncation,
            "pasteurization": args.pasteurization,
            "unitHandling": "VERIFY",
            "nanHandling": args.nan_handling,
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": expression,
    }


def poll_simulation(
    session: requests.Session,
    location: str,
    *,
    max_wait_seconds: int,
) -> dict[str, Any]:
    started = time.monotonic()
    while True:
        response = request_with_backoff(session, "GET", location)
        retry_after = float(response.headers.get("Retry-After") or 5)
        if response.status_code >= 400:
            return {"status": "HTTP_ERROR", "http_status": response.status_code, "body": response.text}

        data = response.json()
        if "alpha" in data or data.get("status") in {"COMPLETE", "ERROR", "FAIL"}:
            return data

        progress = data.get("progress")
        if progress is not None:
            print(f"  progress={progress}", flush=True)

        if time.monotonic() - started > max_wait_seconds:
            data["status"] = "TIMEOUT"
            return data

        time.sleep(retry_after)


def fetch_alpha(session: requests.Session, alpha_id: str) -> dict[str, Any] | None:
    response = request_with_backoff(session, "GET", f"{API_BASE}/alphas/{alpha_id}")
    if response.status_code != 200:
        return None
    return response.json()


def metric(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def summarize(expression: str, result: dict[str, Any], alpha: dict[str, Any] | None) -> dict[str, Any]:
    alpha_id = result.get("alpha") or result.get("alphaId") or metric(result, "result", "alpha")
    source = alpha or result
    checks = metric(source, "is", "checks") or source.get("checks") or result.get("checks") or []
    return {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "expression": expression,
        "status": result.get("status") or ("COMPLETE" if alpha_id else "UNKNOWN"),
        "alpha_id": alpha_id,
        "is_sharpe": metric(source, "is", "sharpe"),
        "is_fitness": metric(source, "is", "fitness"),
        "is_returns": metric(source, "is", "returns"),
        "is_turnover": metric(source, "is", "turnover"),
        "is_margin": metric(source, "is", "margin"),
        "checks": json.dumps(checks, ensure_ascii=False),
    }


def append_csv(path: Path, row: dict[str, Any]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def parse_checks(row: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        checks = json.loads(row.get("checks") or "[]")
    except json.JSONDecodeError:
        return []
    return checks if isinstance(checks, list) else []


def check_names(checks: list[dict[str, Any]], result: str) -> list[str]:
    return [str(check.get("name")) for check in checks if check.get("result") == result]


def is_submittable_candidate(row: dict[str, Any], *, allow_pending_self_correlation: bool) -> bool:
    checks = parse_checks(row)
    failed = check_names(checks, "FAIL")
    pending = check_names(checks, "PENDING")
    if failed:
        return False
    if pending == ["SELF_CORRELATION"] and allow_pending_self_correlation:
        return True
    return not pending


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alphas", type=Path, default=Path("candidates/manual/seed_alphas.txt"))
    parser.add_argument("--out", type=Path, default=Path("runs"))
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Credential env file to load before auth; defaults to .env.",
    )
    parser.add_argument(
        "--no-env-file",
        action="store_true",
        help="Do not load a .env file before auth.",
    )
    parser.add_argument(
        "--auth-method",
        choices=["auto", "password", "cookies"],
        default="auto",
        help="auto uses WQB_EMAIL/WQB_PASSWORD when present, otherwise Chrome cookies.",
    )
    parser.add_argument("--email", default=None, help="WorldQuant BRAIN email; defaults to WQB_EMAIL.")
    parser.add_argument(
        "--password",
        default=None,
        help="WorldQuant BRAIN password. Prefer WQB_PASSWORD or --password-file on servers.",
    )
    parser.add_argument(
        "--password-file",
        type=Path,
        default=None,
        help="File containing the WorldQuant BRAIN password on the first line.",
    )
    parser.add_argument(
        "--no-password-prompt",
        action="store_true",
        help="Fail instead of prompting when password auth lacks a password.",
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-wait-seconds", type=int, default=900)
    parser.add_argument("--pause-seconds", type=float, default=10.0)
    parser.add_argument("--region", default="USA")
    parser.add_argument("--universe", default="TOP3000")
    parser.add_argument("--delay", type=int, default=1)
    parser.add_argument("--decay", type=int, default=4)
    parser.add_argument("--neutralization", default="SUBINDUSTRY")
    parser.add_argument("--truncation", type=float, default=0.08)
    parser.add_argument("--pasteurization", default="ON")
    parser.add_argument("--nan-handling", default="ON")
    parser.add_argument("--stop-after-valid", type=int, default=0)
    parser.add_argument(
        "--strict-self-correlation",
        action="store_true",
        help="Require SELF_CORRELATION to finish before counting a candidate.",
    )
    args = parser.parse_args()

    if not args.no_env_file:
        load_env_file(args.env_file)

    expressions = load_expressions(args.alphas)[: args.limit]
    if not expressions:
        raise SystemExit(f"No expressions found in {args.alphas}")

    run_dir = args.out / utc_stamp()
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.csv"

    session = make_session(args)
    check_auth(session)
    print(f"run_dir={run_dir}", flush=True)
    accepted = 0

    for index, expression in enumerate(expressions, start=1):
        print(f"[{index}/{len(expressions)}] submitting {expression}", flush=True)
        response = request_with_backoff(
            session,
            "POST",
            f"{API_BASE}/simulations",
            json=simulation_payload(expression, args),
        )
        location = response.headers.get("Location")
        if response.status_code != 201 or not location:
            row = {
                "time_utc": datetime.now(timezone.utc).isoformat(),
                "expression": expression,
                "status": f"SUBMIT_HTTP_{response.status_code}",
                "alpha_id": None,
                "is_sharpe": None,
                "is_fitness": None,
                "is_returns": None,
                "is_turnover": None,
                "is_margin": None,
                "checks": response.text[:1000],
            }
            append_csv(summary_path, row)
            print(f"  submit failed: {response.status_code} {response.text[:300]}", flush=True)
            time.sleep(args.pause_seconds)
            continue

        sim_id = location.rstrip("/").split("/")[-1]
        result = poll_simulation(session, location, max_wait_seconds=args.max_wait_seconds)
        (raw_dir / f"{index:03d}_{sim_id}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        alpha_id = result.get("alpha") or result.get("alphaId") or metric(result, "result", "alpha")
        alpha = fetch_alpha(session, alpha_id) if alpha_id else None
        if alpha:
            (raw_dir / f"{index:03d}_{alpha_id}_alpha.json").write_text(
                json.dumps(alpha, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        row = summarize(expression, result, alpha)
        append_csv(summary_path, row)
        checks = parse_checks(row)
        failed = check_names(checks, "FAIL")
        pending = check_names(checks, "PENDING")
        if is_submittable_candidate(
            row,
            allow_pending_self_correlation=not args.strict_self_correlation,
        ):
            accepted += 1
            append_csv(run_dir / "accepted.csv", row)
            print(
                f"  candidate #{accepted}: alpha={row['alpha_id']} pending={pending or 'none'}",
                flush=True,
            )
        elif failed or pending:
            print(f"  checks failed={failed or 'none'} pending={pending or 'none'}", flush=True)
        print(
            "  done status={status} alpha={alpha_id} sharpe={is_sharpe} fitness={is_fitness}".format(
                **row
            ),
            flush=True,
        )
        if args.stop_after_valid and accepted >= args.stop_after_valid:
            print(f"target reached: {accepted} candidates", flush=True)
            break
        time.sleep(args.pause_seconds)

    print(f"summary={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
