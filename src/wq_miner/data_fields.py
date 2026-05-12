from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import brain
from .config import load_config
from .io_utils import load_env_file


def fetch_data_fields(
    session,
    *,
    region: str,
    universe: str,
    delay: int,
    instrument_type: str = "EQUITY",
    page_size: int = 50,
) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    offset = 0
    while True:
        params = {
            "instrumentType": instrument_type,
            "region": region,
            "universe": universe,
            "delay": delay,
            "limit": page_size,
            "offset": offset,
        }
        response = brain.request_with_backoff(
            session, "GET", f"{brain.API_BASE}/data-fields", params=params
        )
        if response.status_code != 200:
            raise SystemExit(
                f"/data-fields failed ({response.status_code}): {response.text[:300]}"
            )
        payload = response.json()
        batch = payload.get("results") or []
        fields.extend(batch)
        total = payload.get("count")
        offset += len(batch)
        if not batch or (isinstance(total, int) and offset >= total):
            break
    return fields


def save_data_fields(
    path: Path,
    *,
    region: str,
    universe: str,
    delay: int,
    fields: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
        "region": region,
        "universe": universe,
        "delay": delay,
        "count": len(fields),
        "fields": fields,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_data_fields(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"fields": [], "fetched_utc": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"fields": [], "fetched_utc": None}
    if not isinstance(data, dict):
        return {"fields": [], "fetched_utc": None}
    data.setdefault("fields", [])
    data.setdefault("fetched_utc", None)
    return data


def available_field_ids(path: Path) -> set[str]:
    data = load_data_fields(path)
    ids: set[str] = set()
    for entry in data.get("fields", []):
        if isinstance(entry, dict) and entry.get("id"):
            ids.add(str(entry["id"]))
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch WorldQuant BRAIN data fields and cache to state/.")
    parser.add_argument("--config", type=Path, default=Path("configs/daily.yaml"))
    parser.add_argument("--no-env-file", action="store_true")
    parser.add_argument("--auth-method", choices=["auto", "password", "cookies"])
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--password-file", type=Path)
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

    fields = fetch_data_fields(
        session,
        region=config.brain.region,
        universe=config.brain.universe,
        delay=config.brain.delay,
    )
    save_data_fields(
        config.state.data_fields,
        region=config.brain.region,
        universe=config.brain.universe,
        delay=config.brain.delay,
        fields=fields,
    )
    print(
        f"saved {len(fields)} fields to {config.state.data_fields} "
        f"(region={config.brain.region} universe={config.brain.universe} delay={config.brain.delay})",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
