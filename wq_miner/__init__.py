"""Development-time package shim for the src layout.

This keeps `python3 -m wq_miner.daily` working from the repository root
without requiring an editable install.
"""

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "wq_miner"
if _SRC_PACKAGE.exists():
    __path__.append(str(_SRC_PACKAGE))  # type: ignore[name-defined]
