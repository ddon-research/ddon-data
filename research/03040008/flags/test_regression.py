"""Regression tests for the flags investigation tooling.

These tests compare generated output against known-good baselines to catch
regressions from refactoring.  The baselines live in ``test_baselines/`` and
were captured from a verified run before any structural changes.
"""
from __future__ import annotations

import orjson
import sys
import unittest
from pathlib import Path

FLAGS_ROOT = Path(__file__).resolve().parent
if str(FLAGS_ROOT) not in sys.path:
    sys.path.insert(0, str(FLAGS_ROOT))

DDON_DATA_ROOT = FLAGS_ROOT.parents[3]
BASELINES_DIR = FLAGS_ROOT / "test_baselines"
GENERATED_DIR = FLAGS_ROOT / "generated"


def _strip_volatile(data: dict) -> dict:
    """Return a copy with timestamp and other volatile fields removed."""
    cleaned = dict(data)
    cleaned.pop("generated_at", None)
    return cleaned


def _load_json(path: Path) -> dict:
    return orjson.loads(path.read_bytes())


class RegressionTests(unittest.TestCase):
    """Compare current generated output against committed baselines."""

    def test_quest_70032001_matches_baseline(self) -> None:
        """The flagship manifest quest should produce identical output."""
        baseline_path = BASELINES_DIR / "quest_70032001_baseline.json"
        generated_path = GENERATED_DIR / "client_investigation_quest_70032001.json"

        self.assertTrue(baseline_path.exists(), f"Baseline not found: {baseline_path}")
        self.assertTrue(generated_path.exists(), f"Generated output not found: {generated_path}")

        baseline = _load_json(baseline_path)
        generated = _strip_volatile(_load_json(generated_path))

        # Compare structure
        self.assertEqual(baseline["format"], generated["format"])
        self.assertEqual(baseline["query"], generated["query"])
        self.assertEqual(len(baseline["targets"]), len(generated["targets"]))

        # Compare each target's hit counts and target metadata
        for i, (b_target, g_target) in enumerate(zip(baseline["targets"], generated["targets"])):
            b_meta = b_target["target"]
            g_meta = g_target["target"]
            self.assertEqual(
                b_meta, g_meta,
                f"Target {i} metadata mismatch: {b_meta} != {g_meta}",
            )
            self.assertEqual(
                len(b_target.get("hits", [])),
                len(g_target.get("hits", [])),
                f"Target {i} (flag={b_meta['flag_value']}) hit count mismatch",
            )
            self.assertEqual(
                len(b_target.get("candidate_hits", [])),
                len(g_target.get("candidate_hits", [])),
                f"Target {i} (flag={b_meta['flag_value']}) candidate count mismatch",
            )

    def test_quest_70032001_structural_integrity(self) -> None:
        """Verify structural properties of a known quest output."""
        generated_path = GENERATED_DIR / "client_investigation_quest_70032001.json"
        if not generated_path.exists():
            self.skipTest("Generated output not found")

        data = _load_json(generated_path)
        self.assertEqual(data["format"], "client_investigation.v4")
        self.assertEqual(data["query"]["mode"], "quest")
        self.assertEqual(data["query"]["value"], 70032001)
        self.assertGreater(len(data["targets"]), 0)

        # Every target should have the expected structure
        for target_report in data["targets"]:
            target = target_report["target"]
            self.assertIn("flag_value", target)
            self.assertIn("flag_type", target)
            self.assertIn("origin", target)
            self.assertIsInstance(target_report.get("hits", []), list)
            self.assertIsInstance(target_report.get("candidate_hits", []), list)

        # Total hits should be substantial for this quest
        total_hits = sum(len(t.get("hits", [])) for t in data["targets"])
        self.assertGreater(total_hits, 100, "Expected significant hit count for quest 70032001")


if __name__ == "__main__":
    unittest.main()
