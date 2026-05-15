from __future__ import annotations

import argparse
import getpass
import os
import sys
import time
from typing import Any

import requests

from .checks import metric


API_BASE = "https://api.worldquantbrain.com"


def base_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "worldquant-daily-miner/0.1",
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
    response = session.post(f"{API_BASE}/authentication", auth=(email, password), timeout=45)
    if response.status_code not in {200, 201}:
        raise SystemExit(
            f"Password authentication failed ({response.status_code}): {response.text[:300]}"
        )
    return session


def load_password(args: argparse.Namespace) -> str | None:
    if getattr(args, "password", None):
        return args.password
    password_file = getattr(args, "password_file", None)
    if password_file:
        return password_file.read_text(encoding="utf-8").splitlines()[0].strip()
    return os.getenv("WQB_PASSWORD") or os.getenv("WORLDQUANT_PASSWORD")


def make_session(args: argparse.Namespace) -> requests.Session:
    email = getattr(args, "email", None) or os.getenv("WQB_EMAIL") or os.getenv("WORLDQUANT_EMAIL")
    password = load_password(args)
    auth_method = getattr(args, "auth_method", "auto")
    no_password_prompt = getattr(args, "no_password_prompt", False)
    if auth_method in {"auto", "password"} and email:
        if password is None and sys.stdin.isatty() and not no_password_prompt:
            password = getpass.getpass(f"WorldQuant BRAIN password for {email}: ")
        if password:
            print("auth_method=password", flush=True)
            return password_session(email, password)
        if auth_method == "password":
            raise SystemExit(
                "Password authentication requires WQB_EMAIL and WQB_PASSWORD "
                "or --email plus --password-file."
            )

    if auth_method in {"auto", "cookies"}:
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
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = session.request(method, url, timeout=45, **kwargs)
        except requests.exceptions.ConnectionError as exc:
            last_exc = exc
            retry_after = min(60, 5 * attempt)
            print(
                f"connection error attempt={attempt}: {type(exc).__name__}; "
                f"sleeping {retry_after:.1f}s",
                flush=True,
            )
            time.sleep(retry_after)
            continue
        if response.status_code != 429:
            return response
        retry_after = float(response.headers.get("Retry-After") or min(60, 5 * attempt))
        print(f"rate limited; sleeping {retry_after:.1f}s", flush=True)
        time.sleep(retry_after)
    if last_exc is not None:
        raise last_exc
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
        retry_after = float(response.headers.get("Retry-After") or 10)
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


def alpha_id_from_result(result: dict[str, Any]) -> str | None:
    alpha_id = result.get("alpha") or result.get("alphaId") or metric(result, "result", "alpha")
    return str(alpha_id) if alpha_id else None
