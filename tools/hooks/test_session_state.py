"""Tests for session_state.py: python -m unittest discover -s tools/hooks

In a scratch root (`HOOK_ROOT`, `HOOK_HOME`, `HOOK_SCRATCHPAD`) with instruction files, open and
done features and a fake `progress.py`: the recording and the resume block of `start`, the diff of
`subagent` (and its cap), the brief copies of `precompact`, and that a subagent's or a broken input
changes nothing and exits 0.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "session_state.py"
TASKS = ("# Tasks\n\n- [x] T1 one\n- [ ] T2 two\n\nNext: an old step.\n\n## Running\n\n- P9 implementer, brief briefs/P9.md\n\n"
         "## Closing\n\n- [ ] C1 close\n\nNext: P9 lands.\n")
FILES = {
    "AGENTS.md": "# Agents\n\n- rule one\n- rule two\n",
    "CLAUDE.md": "@AGENTS.md\n",
    "home/.claude/CLAUDE.md": "# Global\n",
    "specs/002-open/tasks.md": TASKS,
    "specs/002-open/briefs/p2.md": "feature's own p2\n",
    "specs/001-done/tasks.md": "**Status: done**\n\n## Running\n\n- DONE-FEATURE\n",
    "research/knowledge-graph/specs/001-kg/tasks.md": "# KG\n\n- [ ] K1\n",
    "tools/orchestration/progress.py": "print('PROGRESS BLOCK')\n",
    "pad/briefs/p1.md": "pending p1\n",
    "pad/briefs/p2.md": "scratch p2\n",
    "pad/briefs/notes.txt": "not a brief\n",
}


class SessionStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="session_state_")
        self.top = Path(self.tmp.name)
        for name, text in FILES.items():
            (self.top / name).parent.mkdir(parents=True, exist_ok=True)
            (self.top / name).write_text(text, encoding="utf-8", newline="\n")
        self.env = dict(os.environ, HOOK_ROOT=str(self.top), HOOK_HOME=str(self.top / "home"),
                        HOOK_SCRATCHPAD=str(self.top / "pad"))
        self.record = self.top / ".agent-ledger" / "loaded-instructions.json"
        self.main = {"session_id": "s1", "cwd": str(self.top), "hook_event_name": "SessionStart"}
        self.briefs = self.top / "specs" / "002-open" / "briefs"

    def tearDown(self):
        self.tmp.cleanup()

    def hook(self, mode, data):
        text = data if isinstance(data, str) else json.dumps(data)
        done = subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), mode], input=text, capture_output=True,
                              text=True, encoding="utf-8", env=self.env, timeout=120)
        return done.returncode, done.stdout

    @staticmethod
    def context_of(out):
        return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out.strip() else ""

    def test_start_records_only_for_the_main_session(self):
        self.assertEqual(self.hook("start", dict(self.main, agent_id="a1", source="startup")), (0, ""))
        self.assertFalse(self.record.exists())
        self.assertEqual(self.hook("start", dict(self.main, source="startup")), (0, ""))
        files = json.loads(self.record.read_text(encoding="utf-8"))["files"]
        self.assertEqual(len(files), 3)
        self.assertTrue(all(v and len(v["sha256"]) == 64 for v in files.values()))
        self.assertEqual(self.hook("start", dict(self.main, source="clear")), (0, ""))

    def test_start_after_compaction_and_resume(self):
        for source in ("compact", "resume"):
            code, out = self.hook("start", dict(self.main, source=source))
            text = self.context_of(out)
            self.assertEqual(code, 0)
            self.assertIn("PROGRESS BLOCK", text)
            self.assertIn("## specs/002-open/tasks.md: Running", text)
            self.assertIn("- P9 implementer, brief briefs/P9.md", text)
            self.assertIn("last Next: P9 lands.", text)
            self.assertNotIn("an old step", text)
            self.assertNotIn("C1 close", text.split("## specs/002-open/tasks.md: Running")[1].split("last Next")[0])
            self.assertIn("## Open features with no ## Running section and no Next: line\n\n"
                          "- research/knowledge-graph/specs/001-kg", text)
            self.assertNotIn("DONE-FEATURE", text)
            self.assertIn("## git status --short -- tools specs .claude", text)
            self.assertNotIn("worktree", text.lower())
        self.assertTrue(self.record.exists())

    def test_subagent_diff(self):
        self.hook("start", dict(self.main, source="startup"))
        self.assertEqual(self.hook("subagent", {"agent_id": "a2", "agent_type": "implementer"}), (0, ""))
        (self.top / "AGENTS.md").write_text("# Agents\n\n- rule one\n- rule three\n", encoding="utf-8", newline="\n")
        code, out = self.hook("subagent", {"agent_id": "a2"})
        text = self.context_of(out)
        self.assertEqual(code, 0)
        self.assertIn("-- rule two", text)
        self.assertIn("+- rule three", text)
        self.assertIn("AGENTS.md (on disk)", text)
        self.assertNotIn("CLAUDE.md (loaded)", text)
        (self.top / "home" / ".claude" / "CLAUDE.md").unlink()
        self.assertIn("-# Global", self.context_of(self.hook("subagent", {"agent_id": "a2"})[1]))
        (self.top / "AGENTS.md").write_text("".join(f"- new rule {n}\n" for n in range(3000)), encoding="utf-8")
        text = self.context_of(self.hook("subagent", {"agent_id": "a2"})[1])
        self.assertLess(len(text), 12_600)
        self.assertIn("cut at 12000 characters", text)

    def test_subagent_without_record_is_silent(self):
        self.assertEqual(self.hook("subagent", {"agent_id": "a2"}), (0, ""))

    def test_precompact_copies_missing_briefs_only(self):
        self.assertEqual(self.hook("precompact", dict(self.main, agent_id="a3")), (0, ""))
        self.assertFalse((self.briefs / "p1.md").exists())
        code, out = self.hook("precompact", self.main)
        self.assertEqual(code, 0)
        self.assertIn("p1.md", out)
        self.assertIn("specs/002-open/briefs", out)
        self.assertEqual((self.briefs / "p1.md").read_text(encoding="utf-8"), "pending p1\n")
        self.assertEqual((self.briefs / "p2.md").read_text(encoding="utf-8"), "feature's own p2\n")
        self.assertFalse((self.briefs / "notes.txt").exists())
        self.assertTrue((self.top / "pad" / "briefs" / "p1.md").exists(), "the scratchpad copy is kept")
        self.assertEqual(self.hook("precompact", self.main), (0, ""))

    def test_precompact_with_two_open_root_features_copies_nothing(self):
        (self.top / "specs" / "003-other").mkdir()
        (self.top / "specs" / "003-other" / "tasks.md").write_text("- [ ] X\n", encoding="utf-8")
        self.assertEqual(self.hook("precompact", self.main), (0, ""))
        self.assertFalse((self.briefs / "p1.md").exists())
        (self.top / ".specify").mkdir()
        (self.top / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/003-other"}),
                                                           encoding="utf-8")
        self.hook("precompact", self.main)
        self.assertTrue((self.top / "specs" / "003-other" / "briefs" / "p1.md").exists())
        self.assertFalse((self.briefs / "p1.md").exists())

    def test_broken_input_exits_0_silently(self):
        for mode in ("start", "subagent", "precompact", ""):
            for text in ("not json", "[1, 2]"):
                self.assertEqual(self.hook(mode, text), (0, ""))
        self.assertFalse(self.record.exists())


if __name__ == "__main__":
    unittest.main()
