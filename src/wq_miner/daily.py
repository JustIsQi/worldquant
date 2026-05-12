from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from . import brain
from .candidates import (
    build_candidate_pool,
    failed_entries_from_summary,
    failed_history_expressions,
    write_candidates,
)
from .config import load_config
from .io_utils import load_env_file
from .report import generate_report, trailing_week_active_count
from .data_fields import available_field_ids
from .runner import make_run_dir, run_candidates
from .state import (
    active_expressions,
    active_ids,
    add_skip_expressions,
    load_skip_entries,
    load_skip_history,
    save_skip_history,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/daily.yaml"))
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--already-active", action="append", default=[])
    parser.add_argument("--no-env-file", action="store_true")
    parser.add_argument("--auth-method", choices=["auto", "password", "cookies"])
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--password-file", type=Path)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    run_date = date.fromisoformat(args.date)
    run_dir = make_run_dir(config, run_date)
    run_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_env_file:
        load_env_file(config.auth.env_file)

    skip = load_skip_history(config.state.skip_history)
    if not skip and config.candidates.filter_failed_history:
        skip = failed_history_expressions(config.run.out_dir)
        if skip:
            save_skip_history(config.state.skip_history, skip)
            print(f"skip_history_bootstrap={len(skip)}", flush=True)
    skip |= active_expressions(config.state.active_alphas)

    data_fields_path = config.state.data_fields
    available = available_field_ids(data_fields_path) if data_fields_path.exists() else set()
    if not available:
        print(
            f"warning: {data_fields_path} missing or empty; "
            f"run `python -m wq_miner.data_fields --config {args.config}` to populate. "
            f"Skipping field-existence filter for this run.",
            flush=True,
        )

    expressions = build_candidate_pool(
        config.candidates,
        runs_dir=config.run.out_dir,
        skip_expressions=skip,
        available_fields=available or None,
    )
    candidate_path = run_dir / config.candidates.generated_output_name
    write_candidates(candidate_path, expressions)
    print(f"candidates={candidate_path}", flush=True)
    print(f"candidate_count={len(expressions)} skip_set_size={len(skip)}", flush=True)

    known_active = active_ids(config.state.active_alphas) | set(args.already_active)
    weekly_active = trailing_week_active_count(config.run.out_dir, today=run_date)
    if args.dry_run:
        report_path = generate_report(
            run_dir,
            target_active=config.run.target_active,
            already_active=len(known_active),
            dry_run=True,
            candidate_count=len(expressions),
            target_active_per_week=config.run.target_active_per_week,
            weekly_active=weekly_active,
            families=config.candidates.families,
            historical_skip_entries=load_skip_entries(config.state.skip_history),
        )
        print(f"run_dir={run_dir}", flush=True)
        print(f"report={report_path}", flush=True)
        return 0

    auth_args = argparse.Namespace(
        auth_method=args.auth_method or config.auth.auth_method,
        email=args.email or config.auth.email,
        password=args.password or config.auth.password,
        password_file=args.password_file or config.auth.password_file,
        no_password_prompt=True,
    )
    check_session = brain.make_session(auth_args)
    brain.check_auth(check_session)

    run_candidates(
        config=config,
        expressions=expressions,
        already_active=known_active,
        auth_args=auth_args,
        run_dir=run_dir,
    )
    new_failed = failed_entries_from_summary(
        run_dir / "submit_summary.csv",
        families=config.candidates.families,
    )
    if new_failed:
        add_skip_expressions(config.state.skip_history, new_failed)
        print(f"skip_history_added={len(new_failed)}", flush=True)
    weekly_active = trailing_week_active_count(config.run.out_dir, today=run_date)
    report_path = generate_report(
        run_dir,
        target_active=config.run.target_active,
        already_active=len(known_active),
        target_active_per_week=config.run.target_active_per_week,
        weekly_active=weekly_active,
        families=config.candidates.families,
        historical_skip_entries=load_skip_entries(config.state.skip_history),
    )
    print(f"report={report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
