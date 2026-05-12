from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wq_miner.candidates import (
    build_candidate_pool,
    family_of,
    generate_rule_candidates,
)
from wq_miner.config import CandidateConfig, FamilyConfig
from wq_miner.io_utils import dedupe, load_expressions


def _candidate_config(**overrides) -> CandidateConfig:
    defaults = dict(
        manual_globs=[],
        template_files=[],
        filter_failed_history=False,
        per_family_max=0,
        interleave=False,
        mix_weights=[0.6],
        price_mix_component="-rank(ts_delta(close,5))",
        families={
            "leverage": FamilyConfig(
                name="leverage",
                builder="simple_rank",
                fields=["debt/assets"],
                mix_with_price=True,
            ),
        },
    )
    defaults.update(overrides)
    return CandidateConfig(**defaults)


class CandidateTests(unittest.TestCase):
    def test_load_expressions_ignores_comments_and_blanks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alphas.txt"
            path.write_text("\n# comment\nrank(close)\n\n rank(volume) \n", encoding="utf-8")
            self.assertEqual(load_expressions(path), ["rank(close)", "rank(volume)"])

    def test_dedupe_normalizes_whitespace(self) -> None:
        self.assertEqual(
            dedupe(["rank(close)", " rank(close) ", "rank(volume)"]),
            ["rank(close)", "rank(volume)"],
        )

    def test_build_candidate_pool_includes_manual_and_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manual = root / "manual.txt"
            manual.write_text("rank(close)\n", encoding="utf-8")
            config = _candidate_config(manual_globs=[str(manual)])
            expressions = build_candidate_pool(config, runs_dir=root / "runs")
        self.assertIn("rank(close)", expressions)
        self.assertIn("rank(debt/assets)", expressions)
        self.assertIn("0.6*rank(debt/assets)+0.4*(-rank(ts_delta(close,5)))", expressions)

    def test_build_candidate_pool_skips_provided_expressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manual = root / "manual.txt"
            manual.write_text("rank(close)\n  rank(volume) \n", encoding="utf-8")
            config = _candidate_config(manual_globs=[str(manual)], families={})
            expressions = build_candidate_pool(
                config,
                runs_dir=root / "runs",
                skip_expressions={"rank(close)"},
            )
        self.assertNotIn("rank(close)", expressions)
        self.assertIn("rank(volume)", expressions)

    def test_generate_rule_candidates_interleaves_families(self) -> None:
        config = _candidate_config(
            interleave=True,
            mix_weights=[],
            families={
                "a": FamilyConfig(name="a", builder="simple_rank", fields=["alpha1"]),
                "b": FamilyConfig(name="b", builder="simple_rank", fields=["bravo1"]),
            },
        )
        exprs = generate_rule_candidates(config)
        # First two should come from different families (interleaved).
        self.assertEqual(exprs[0], "alpha1")
        self.assertEqual(exprs[1], "bravo1")

    def test_generate_rule_candidates_per_family_cap(self) -> None:
        config = _candidate_config(
            per_family_max=2,
            mix_weights=[],
            families={
                "leverage": FamilyConfig(
                    name="leverage",
                    builder="simple_rank",
                    fields=["debt/assets", "debt_lt/assets"],
                ),
            },
        )
        exprs = generate_rule_candidates(config)
        self.assertEqual(len(exprs), 2)

    def test_generate_rule_candidates_filters_unavailable_fields(self) -> None:
        config = _candidate_config(
            mix_weights=[],
            families={
                "leverage": FamilyConfig(
                    name="leverage",
                    builder="simple_rank",
                    fields=["debt/assets", "ghost/field"],
                ),
            },
        )
        exprs = generate_rule_candidates(
            config, available_fields={"debt", "assets"}
        )
        # debt/assets keeps; ghost/field dropped because "ghost" not available.
        for e in exprs:
            self.assertNotIn("ghost", e)
        self.assertIn("rank(debt/assets)", exprs)

    def test_generate_rule_candidates_disabled_family(self) -> None:
        config = _candidate_config(
            mix_weights=[],
            families={
                "leverage": FamilyConfig(
                    name="leverage",
                    builder="simple_rank",
                    fields=["debt/assets"],
                    enabled=False,
                ),
            },
        )
        self.assertEqual(generate_rule_candidates(config), [])

    def test_family_of_matches_substring(self) -> None:
        families = {
            "leverage": FamilyConfig(
                name="leverage", builder="simple_rank", fields=["debt/assets"]
            ),
            "value": FamilyConfig(
                name="value", builder="simple_rank", fields=["bookvalue_ps/close"]
            ),
        }
        self.assertEqual(family_of("rank(debt/assets)", families), "leverage")
        self.assertEqual(family_of("0.6*rank(bookvalue_ps/close)+0.4*x", families), "value")
        self.assertIsNone(family_of("rank(unknown_field)", families))


if __name__ == "__main__":
    unittest.main()
