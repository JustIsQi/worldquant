from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wq_miner.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_defaults_and_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "daily.yaml"
            path.write_text(
                """
brain:
  decay: 12
run:
  target_active: 5
  daily_budget_minutes: 30
  auto_submit: false
candidates:
  manual_globs: ["a/*.txt", "b/*.txt"]
  mix_weights: [0.8, 0.2]
""",
                encoding="utf-8",
            )
            config = load_config(path)

        self.assertEqual(config.brain.region, "USA")
        self.assertEqual(config.brain.decay, 12)
        self.assertEqual(config.run.target_active, 5)
        self.assertEqual(config.run.daily_budget_minutes, 30)
        self.assertFalse(config.run.auto_submit)
        self.assertEqual(config.candidates.manual_globs, ["a/*.txt", "b/*.txt"])
        self.assertEqual(config.candidates.mix_weights, [0.8, 0.2])
        # Default families populated when no candidates.families block provided.
        self.assertIn("leverage", config.candidates.families)
        self.assertIn("quality", config.candidates.families)
        self.assertEqual(config.candidates.per_family_max, 8)

    def test_load_families_from_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "daily.yaml"
            path.write_text(
                """
candidates:
  per_family_max: 4
  interleave: false
  families:
    custom_a:
      enabled: true
      builder: simple_rank
      mix_with_price: true
      fields: ["x/y", "z"]
    custom_b:
      enabled: false
      builder: signal_passthrough
      fields: ["-ts_delta(close,3)"]
""",
                encoding="utf-8",
            )
            config = load_config(path)
        self.assertEqual(set(config.candidates.families.keys()), {"custom_a", "custom_b"})
        self.assertTrue(config.candidates.families["custom_a"].mix_with_price)
        self.assertFalse(config.candidates.families["custom_b"].enabled)
        self.assertEqual(config.candidates.families["custom_a"].fields, ["x/y", "z"])
        self.assertEqual(config.candidates.per_family_max, 4)
        self.assertFalse(config.candidates.interleave)

    def test_legacy_flat_yaml_back_compat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "daily.yaml"
            path.write_text(
                """
candidates:
  fundamental_fields: ["debt/assets"]
  value_fields: ["bookvalue_ps/close"]
  price_components: ["-rank(ts_delta(close,5))"]
""",
                encoding="utf-8",
            )
            config = load_config(path)
        # legacy synthesized into 3 families.
        self.assertIn("leverage", config.candidates.families)
        self.assertIn("value", config.candidates.families)
        self.assertIn("reversal_short", config.candidates.families)
        self.assertEqual(
            config.candidates.families["leverage"].fields, ["debt/assets"]
        )


if __name__ == "__main__":
    unittest.main()
