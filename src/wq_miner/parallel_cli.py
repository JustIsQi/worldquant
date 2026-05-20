from __future__ import annotations

import argparse
import csv
from pathlib import Path

from . import brain
from .config import AuthConfig, BrainConfig, CandidateConfig, DailyConfig, RunConfig, StateConfig
from .io_utils import load_env_file, load_expressions, utc_stamp
from .report import generate_report
from .runner import run_candidates


def load_processed(path: Path | None) -> set[int]:
    if not path or not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            int(row["source_index"])
            for row in csv.DictReader(handle)
            if (row.get("source_index") or "").isdigit()
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alphas", type=Path, default=Path("candidates/manual/candidate_alphas.txt"))
    parser.add_argument("--out", type=Path, default=Path("runs"))
    parser.add_argument("--resume-summary", type=Path)
    parser.add_argument("--skip-before", type=int, default=1)
    parser.add_argument("--target-active", type=int, default=3)
    parser.add_argument("--already-active", action="append", default=[])
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-inflight", type=int, default=3)
    parser.add_argument("--max-wait-seconds", type=int, default=900)
    parser.add_argument("--submit-poll-seconds", type=int, default=90)
    parser.add_argument("--submit-poll-interval", type=float, default=10.0)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--no-env-file", action="store_true")
    parser.add_argument("--auth-method", choices=["auto", "password", "cookies"], default="auto")
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--password-file", type=Path)
    parser.add_argument("--region", default="USA")
    parser.add_argument("--universe", default="TOP3000")
    parser.add_argument("--delay", type=int, default=1)
    parser.add_argument("--decay", type=int, default=4)
    parser.add_argument("--neutralization", default="SUBINDUSTRY")
    parser.add_argument("--truncation", type=float, default=0.08)
    parser.add_argument("--pasteurization", default="ON")
    parser.add_argument("--nan-handling", default="ON")
    parser.add_argument("--no-submit", action="store_true")
    args = parser.parse_args(argv)

    if not args.no_env_file:
        load_env_file(args.env_file)

    config = DailyConfig(
        auth=AuthConfig(
            env_file=args.env_file,
            auth_method=args.auth_method,
            email=args.email,
            password=args.password,
            password_file=args.password_file,
        ),
        brain=BrainConfig(
            region=args.region,
            universe=args.universe,
            delay=args.delay,
            decay=args.decay,
            neutralization=args.neutralization,
            truncation=args.truncation,
            pasteurization=args.pasteurization,
            nan_handling=args.nan_handling,
            max_wait_seconds=args.max_wait_seconds,
            submit_poll_seconds=args.submit_poll_seconds,
            submit_poll_interval=args.submit_poll_interval,
        ),
        run=RunConfig(
            out_dir=args.out,
            target_active=args.target_active,
            workers=args.workers,
            max_inflight=args.max_inflight,
            auto_submit=not args.no_submit,
            skip_before=args.skip_before,
        ),
        candidates=CandidateConfig(),
        state=StateConfig(),
    )
    auth_args = argparse.Namespace(
        auth_method=args.auth_method,
        email=args.email,
        password=args.password,
        password_file=args.password_file,
        no_password_prompt=True,
    )
    check_session = brain.make_session(auth_args)
    brain.check_auth(check_session)
    processed = load_processed(args.resume_summary)
    expressions = [
        expression
        for index, expression in enumerate(load_expressions(args.alphas), start=1)
        if index not in processed
    ]
    run_dir = args.out / f"{utc_stamp()}_parallel_submit_goal"
    run_candidates(
        config=config,
        expressions=expressions,
        already_active=set(args.already_active),
        auth_args=auth_args,
        run_dir=run_dir,
    )
    report_path = generate_report(run_dir, target_active=args.target_active, already_active=len(args.already_active))
    print(f"report={report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
