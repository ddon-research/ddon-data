"""Tests for progress.py: python -m unittest discover -s tools/orchestration"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import progress  # noqa: E402
import retro  # noqa: E402


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", "-c", "user.name=t", "-c", "user.email=t@t",
                    *args], check=True, capture_output=True)


def response(mid, stamp, context, model="claude-opus-5-5"):
    usage = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": context, "output_tokens": 0}
    return json.dumps({"type": "assistant", "timestamp": stamp, "message": {"id": mid, "model": model, "usage": usage}})


class ProgressTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        for folder, text in (("specs/001-done", "**Status**: Closed.\n- [X] T1\n"),
                             ("specs/002-open", "# Tasks\n- [x] T1\n- [x] T2\n- [ ] T3\n  - [ ] T3a: then `**Status: done**`\n"),
                             ("specs/003-said-done", "**Status: done**\n- [x] T1\n"),
                             ("research/knowledge-graph/specs/004-kg", "- [ ] K1\n")):
            (self.repo / folder).mkdir(parents=True)
            (self.repo / folder / "tasks.md").write_text(text, encoding="utf-8")
        git(self.repo, "init", "-q")
        git(self.repo, "add", "specs")
        git(self.repo, "commit", "-q", "-m", "init", "--date", "2026-10-17T07:00:00Z")
        self.projects = self.root / "projects"
        self.projects.mkdir()
        self.ledger = self.root / "ledger"
        self.ledger.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_features_skip_done_ones(self):
        found = progress.features(self.repo)
        self.assertEqual(found, [("specs/002-open", 2, 2), ("research/knowledge-graph/specs/004-kg", 0, 1)])

    def test_block(self):
        (self.projects / "s1.jsonl").write_text(response("r1", "2026-10-17T08:00:00Z", 100_000) + "\n"
                                                + response("r2", "2026-10-17T08:01:00Z", 500_000) + "\n", encoding="utf-8")
        (self.ledger / "usage-readings.jsonl").write_text(
            json.dumps({"at": "a", "weekly": 10}) + "\nbad\n"
            + json.dumps({"at": "2026-10-17T09:00:00+02:00", "weekly": 34, "weekly_resets_at": "R", "five_hour": 12})
            + "\n", encoding="utf-8")
        text = progress.block(self.repo, self.projects, self.ledger)
        lines = text.splitlines()
        self.assertLessEqual(len(lines), 10)
        self.assertIn("- specs/002-open: [#####-----] 2 done, 2 open · since 2026-10-17: $0.12, coordinator 100%, 0 agents",
                      text)
        self.assertIn("004-kg: [----------] 0 done, 1 open · spend unavailable (no commit touches the folder", text)
        self.assertIn("usage: weekly 34% (resets R), 5-hour 12%", text)
        self.assertIn("context: 500k of 1,000k (50%) · $0.10 a turn in cache reads", text)
        self.assertNotIn("001-done", text)

    def test_since_overrides_the_first_commit(self):
        (self.projects / "s1.jsonl").write_text(response("r1", "2026-10-17T08:00:00Z", 100_000) + "\n", encoding="utf-8")
        text = progress.block(self.repo, self.projects, self.ledger, retro.moment("2026-10-18"))
        self.assertIn("since 2026-10-18: $0.00, 0 agents", text)
        self.assertNotIn("spend unavailable", text)

    def test_nothing_to_read(self):
        text = progress.block(self.repo, self.projects / "none", self.ledger)
        self.assertIn("usage: unavailable", text)
        self.assertIn("context: unavailable", text)

    def test_context_after_a_compaction_is_unavailable(self):
        path = self.projects / "s1.jsonl"
        path.write_text(response("r1", "2026-10-17T08:00:00Z", 900_000) + "\n"
                        + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n", encoding="utf-8")
        self.assertIsNone(progress.last_response(path))
        path.write_text(response("r1", "2026-10-17T08:00:00Z", 900_000, model="claude-new-9") + "\n", encoding="utf-8")
        self.assertIn("$ unavailable (no price for claude-new-9)", progress.context_text(self.projects))


if __name__ == "__main__":
    unittest.main()
