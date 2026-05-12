#!/usr/bin/env python3
"""Compatibility wrapper for the daily miner parallel submit command."""

from __future__ import annotations

from wq_miner.parallel_cli import main


if __name__ == "__main__":
    raise SystemExit(main())
