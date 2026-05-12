from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wq_miner.daily import main


class DailyDryRunTests(unittest.TestCase):
    def test_daily_dry_run_generates_candidates_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manual = root / "manual.txt"
            manual.write_text("liabilities/assets\n", encoding="utf-8")
            config = root / "daily.yaml"
            config.write_text(
                f"""
run:
  out_dir: {root / "runs"}
candidates:
  manual_globs: ["{manual}"]
  template_files: []
  filter_failed_history: false
state:
  active_alphas: {root / "active.json"}
  skip_history: {root / "skip_history.json"}
  data_fields: {root / "data_fields.json"}
""",
                encoding="utf-8",
            )
            result = main(["--config", str(config), "--date", "2026-05-11", "--dry-run"])
            reports = list((root / "runs" / "2026-05-11").glob("*_daily/report.md"))
            candidates = list((root / "runs" / "2026-05-11").glob("*_daily/candidates.txt"))
            report_text = reports[0].read_text(encoding="utf-8")

            self.assertEqual(result, 0)
            self.assertEqual(len(reports), 1)
            self.assertEqual(len(candidates), 1)
            self.assertIn("Dry run", report_text)


if __name__ == "__main__":
    unittest.main()
