from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wq_miner.report import generate_report


class ReportTests(unittest.TestCase):
    def test_generate_report_from_submit_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "submit_summary.csv").write_text(
                "time_utc,source_index,expression,sim_status,alpha_id,alpha_status,sharpe,fitness,returns,turnover,margin,submit_http_status,submit_check_http_status,submit_result,failed,pending,note\n"
                'now,1,liabilities/assets,COMPLETE,a1,ACTIVE,1.5,1.2,0.1,0.02,0.01,201,200,ACTIVE,[],[],""\n'
                'now,2,rank(close),COMPLETE,a2,UNSUBMITTED,0.5,0.2,0.01,0.8,0.0,,,SKIPPED_CHECKS,"[""LOW_FITNESS""]",[],""\n',
                encoding="utf-8",
            )
            report = generate_report(run_dir, target_active=3, already_active=1)
            text = report.read_text(encoding="utf-8")

        self.assertIn("今日结论", text)
        self.assertIn("liabilities/assets", text)
        self.assertIn("LOW_FITNESS", text)


if __name__ == "__main__":
    unittest.main()
