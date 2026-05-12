from __future__ import annotations

import unittest

from wq_miner.checks import check_lists, is_submittable


class CheckTests(unittest.TestCase):
    def test_check_lists_and_submittable(self) -> None:
        checks = [
            {"name": "LOW_SHARPE", "result": "PASS"},
            {"name": "SELF_CORRELATION", "result": "PENDING"},
        ]
        failed, pending = check_lists(checks)
        self.assertEqual(failed, [])
        self.assertEqual(pending, ["SELF_CORRELATION"])
        self.assertTrue(is_submittable(failed, pending))

    def test_failed_check_is_not_submittable(self) -> None:
        self.assertFalse(is_submittable(["LOW_FITNESS"], ["SELF_CORRELATION"]))
        self.assertFalse(is_submittable([], ["OTHER_PENDING"]))


if __name__ == "__main__":
    unittest.main()
