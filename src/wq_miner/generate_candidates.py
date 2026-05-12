from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .candidates import build_candidate_pool, write_candidates
from .config import load_config
from .state import active_expressions, load_skip_history


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/daily.yaml"))
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    skip = load_skip_history(config.state.skip_history) | active_expressions(config.state.active_alphas)
    expressions = build_candidate_pool(
        config.candidates,
        runs_dir=config.run.out_dir,
        skip_expressions=skip or None,
    )
    out = args.out or config.run.out_dir / args.date / config.candidates.generated_output_name
    write_candidates(out, expressions)
    print(f"candidates={out}", flush=True)
    print(f"count={len(expressions)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
