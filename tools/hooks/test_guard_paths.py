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
EXTENDED = "\\\\?\\"


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

    def test_dot_dot_cannot_hide_a_refused_path(self):
        for path in (f"{REPO}/packets/patterns/../decrypted_json/x.json", f"{REPO}/docs/../AGENTS.md",
                     f"{REPO}\\packets\\patterns\\..\\decrypted_json\\x.json"):
            with self.subTest(path=path):
                self.assertIsNotNone(guard_paths.verdict(edit(path, REPO), "--deny-owned", []))
        self.assertIsNone(guard_paths.verdict(edit(f"{REPO}/packets/decrypted_json/../patterns/x.md", REPO), "--deny-owned", []))

    def test_every_spelling_of_data_and_owned_paths_is_refused(self):
        lower = REPO.lower()
        bare = REPO.split(":", 1)[1]  # /ddon-data
        drive = REPO[0].lower()
        for tail in ("client/x.json", "packets/decrypted_json/x", "AGENTS.md", ".claude/settings.json",
                     "specs/009-docs-structure/tasks.md"):
            cased = tail.upper() if tail[0] != "s" else tail.replace("tasks", "TASKS")
            for path in (f"{REPO}/{tail}", f"{lower}/{tail}", f"{REPO}/{cased}", f"/{drive}{bare}/{tail}",
                         f"/mnt/{drive}{bare}/{tail}", tail, f"./{tail}", f"//?/{REPO}/{tail}",
                         "\\?\\" + f"{REPO}/{tail}".replace("/", "\\"), f"docs/../{tail}", f"{REPO}/{tail}.",
                         f"{REPO}/{tail} ", f"{REPO}/{tail}::$DATA", f"{REPO}//{tail}"):
                with self.subTest(path=path):
                    self.assertIsNotNone(guard_paths.verdict(edit(path, REPO), "--deny-owned", []))
        self.assertIsNotNone(guard_paths.verdict(edit("decrypted_raw/x", f"{REPO}/packets"), "--deny-owned", []))
        self.assertIsNotNone(guard_paths.verdict(edit("../client/x", f"{REPO}/docs"), "--deny-owned", []))
        self.assertIsNotNone(guard_paths.verdict(edit("client/x", f"/{drive}{bare}"), "--deny-owned", []))
        self.assertIsNotNone(guard_paths.verdict(edit("client/x", None), "--deny-owned", []))

    def test_patterns_stay_writable_by_every_spelling(self):
        lower = REPO.lower()
        bare = REPO.split(":", 1)[1]
        drive = REPO[0].lower()
        tail = "packets/patterns/03040008/x-pattern.cpp"
        for path in (f"{REPO}/{tail}", f"{lower}/{tail}", f"{REPO}/{tail.upper()}", f"/{drive}{bare}/{tail}",
                     f"/mnt/{drive}{bare}/{tail}", tail, f"./{tail}", f"//?/{REPO}/{tail}",
                     "\\?\\" + f"{REPO}/{tail}".replace("/", "\\"), f"{REPO}/packets/decrypted_json/../patterns/x.md"):
            with self.subTest(path=path):
                self.assertIsNone(guard_paths.verdict(edit(path, REPO), "--deny-owned", []))
        self.assertIsNone(guard_paths.verdict(edit("patterns/x.md", f"{REPO}/packets"), "--deny-owned", []))

    def test_allow_list_only_tightens(self):
        allow = ["specs/*/research/*"]
        for path in ("specs/x/research/y", f"/d{REPO[2:]}/specs/x/research/y", f"{REPO}/SPECS/x/research/y",
                     f"//?/{REPO}/specs/x/research/y", f"{REPO}/specs/x/research/../../../client/x"):
            with self.subTest(path=path):
                self.assertIsNotNone(guard_paths.verdict(edit(path, REPO), "--allow", allow))
        self.assertIsNone(guard_paths.verdict(edit(f"{REPO}/specs/x/research/y", REPO), "--allow", allow))

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
