"""Tests for guard_paths.py: python -m unittest discover -s tools/hooks"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import guard_paths  # noqa: E402
import hooklib  # noqa: E402

REPO = str(hooklib.REPO).replace("\\", "/")
WORKTREE = f"{REPO}/.claude/worktrees/agent-1"


def edit(path, cwd=WORKTREE):
    return {"tool_name": "Edit", "cwd": cwd, "tool_input": {"file_path": path}}


class GuardPathsTest(unittest.TestCase):
    def test_owned_files_are_refused_in_worktree_and_main_checkout(self):
        for rel in ("AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".claude/agents/implementer.md",
                    "specs/010-agentic-practices/tasks.md", ".specify/memory/constitution.md",
                    "specs/orchestration.md"):
            for root in (WORKTREE, REPO):
                with self.subTest(rel=rel, root=root):
                    self.assertIsNotNone(guard_paths.verdict(edit(f"{root}/{rel}"), "--deny-owned", []))
        windows = f"{WORKTREE}/AGENTS.md".replace("/", "\\")
        self.assertIsNotNone(guard_paths.verdict(edit(windows), "--deny-owned", []))

    def test_other_files_pass_deny_mode(self):
        for rel in ("src/core/x.cpp", "specs/010-agentic-practices/spec.md", "docs/AGENTS.md.txt", "test/a.cpp"):
            with self.subTest(rel=rel):
                self.assertIsNone(guard_paths.verdict(edit(f"{WORKTREE}/{rel}"), "--deny-owned", []))
        self.assertIsNone(guard_paths.verdict(edit("C:/Temp/scratch/AGENTS.md", cwd="C:/Temp"), "--deny-owned", []))

    def test_allow_mode(self):
        allow = ["specs/*/research/*"]
        self.assertIsNone(guard_paths.verdict(edit(f"{REPO}/specs/010-x/research/a.md", REPO), "--allow", allow))
        self.assertIsNotNone(guard_paths.verdict(edit(f"{REPO}/src/a.cpp", REPO), "--allow", allow))
        self.assertIsNotNone(guard_paths.verdict(edit("C:/Temp/a.md", REPO), "--allow", allow))

    def test_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, DDON_HOOK_LEDGER_DIR=tmp)
            run = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HERE / "guard_paths.py"), "--deny-owned"],
                                 input=json.dumps(edit(f"{WORKTREE}/CLAUDE.md")), capture_output=True, text=True,
                                 env=env)
            self.assertEqual(run.returncode, 2)
            self.assertIn("coordinator", run.stderr)


if __name__ == "__main__":
    unittest.main()
