"""Tests for guard_bash.py: python -m unittest discover -s tools/hooks"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import guard_bash  # noqa: E402

REFUSED = [
    "grep -rn foo src",
    "git ls-files | grep hook",
    "timeout 30 egrep x f",
    "ls | xargs grep foo",
    "find . -name '*.cpp'",
    "du -sh build",
    "sed -i 's/a/b/' f.txt",
    "sed -E -i.bak 's/a/b/' f.txt",
    "cat src/x.cpp | head -50",
    "cat f | tail -n 5",
    "sd -F 'a;\n' '' f.cpp",
    "git commit --no-gpg-sign -m x",
    "git -c commit.gpgsign=false commit -m x",
    "git commit --no-verify -m x",
    "git commit -n -m x",
    "git commit -am 'msg'",
    "git commit -a -m x",
    "git add -A",
    "git add .",
    "git add -u",
    "git add --all src",
    "git add src/a.cpp && git add :/",
    "git push --force origin rng-monitor",
    "git push -f",
    "git push --force-with-lease origin rng-monitor",
    "git push origin :rng-monitor",
    "git push origin +rng-monitor",
    "git push origin main",
    "git push origin rng-monitor:main",
    "git push --delete origin old",
    "while true; do sleep 5; done",
    "until rg -q done log.txt; do sleep 10; done",
    "echo ok\ngrep x f",
    "git commit -q -F - <<'EOF'\nmsg isn't here\nEOF\ngit push --force origin main",
    # ddon-data: worktrees, large trees, bulk reverts
    "git worktree add ../wt -b x",
    "git -C D:/ddon-data worktree add C:/wt/a",
    "git diff",
    "git diff HEAD~1",
    "git diff -- client/03040008",
    "git diff --cached -- packets/decrypted_json",
    "git log -p -3",
    "git ls-files client",
    "ls -R client/03040008",
    "fd -e json . client/03040008",
    "tree packets",
    "rg -n ItemId client/03040008",
    "rg --files /d/ddon-data/client",
    "rg -n x D:/ddon-data/packets/decrypted_json",
    "git checkout -- .",
    "git checkout -- client/",
    "git checkout .",
    "git restore research/",
    "git restore -- 'research/*.py'",
    "git rm -r research/old",
]

ALLOWED = [
    "rg -n foo src",
    "git grep -n foo",
    "fd -e cpp . src",
    "sed -n 1,5p f.txt",
    "rg -m 5 x f | head -3",
    "git log --oneline -5 | head",
    "head -20 f.txt",
    "sd -F 'a' 'b' f.cpp",
    "sd -A 'a\nb' '' f.cpp",
    "git commit -m 'grep, find and sed -i are refused'",
    "git commit -q -F - <<'EOF'\nuse git add -A and git push --force\nEOF",
    "git commit -m '-a is not a flag here'",
    "git -c core.autocrlf=false commit -m x",
    "git add src/a.cpp tools/hooks/guard_bash.py",
    "git add -- 'docs/index.md'",
    "git push",
    "git push origin rng-monitor",
    "git push -u origin HEAD",
    "git push origin refs/tags/v1",
    "git push origin --tags",
    "cmake --build --preset x86-debug-vs2026",
    "echo 'while true; do sleep 1; done'",
    "",
    # ddon-data: bounded forms
    "git worktree list",
    "git diff --stat -- client/03040008",
    "git diff --name-only HEAD~1",
    "git diff -- research/03040008/flags/README.md",
    "git diff | wc -l",
    "git log --oneline -5",
    "git log -p -3 -- tools/hooks/guard_bash.py",
    "git ls-files client | wc -l",
    "fd -d 2 . client/03040008",
    "rg -c ItemId client/03040008",
    "rg -l -m 1 ItemId client/03040008/quest",
    "rg --files client | wc -l",
    "rg -n x research packets/decrypt-annotate-streams.sh",
    "dust -d 1 client",
    "ls client",
    "git checkout main",
    "git checkout -b feature",
    "git checkout -- research/03040008/flags/README.md",
    "git restore --staged research/x.py",
    "git rm research/old.txt",
]


def data(command, tool="Bash", agent="a1", call="c"):
    return {"tool_name": tool, "tool_input": {"command": command}, "cwd": ".", "session_id": "s",
            "agent_id": agent, "tool_use_id": call}


class GuardBashTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"DDON_HOOK_POLL_DIR": self.tmp.name,
                                                "DDON_HOOK_LEDGER_DIR": self.tmp.name})
        self.env.start()
        self.branch = mock.patch.object(guard_bash, "current_branch", return_value="rng-monitor")
        self.branch.start()

    def tearDown(self):
        self.branch.stop()
        self.env.stop()
        self.tmp.cleanup()

    def test_refused(self):
        for index, command in enumerate(REFUSED):
            with self.subTest(command=command):
                self.assertIsNotNone(guard_bash.verdict(data(command, call=f"r{index}")))

    def test_allowed(self):
        for index, command in enumerate(ALLOWED):
            with self.subTest(command=command):
                self.assertIsNone(guard_bash.verdict(data(command, agent=f"x{index}", call=f"a{index}")))

    def test_git_add_directory(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "specs" / "011").mkdir(parents=True)
            (Path(root) / "specs" / "011" / "tasks.md").write_text("x", encoding="utf-8")
            check = lambda command: guard_bash.check_git(command.split(), root)  # noqa: E731
            self.assertIsNotNone(check("git add specs"))
            self.assertIsNotNone(check("git add specs/011 specs/011/tasks.md"))
            self.assertIsNotNone(check(f"git -C {root} add specs"))
            self.assertIsNone(check("git add specs/011/tasks.md"))
            self.assertIsNone(check("git add -- specs/011/tasks.md missing.txt"))

    def test_powershell(self):
        self.assertIsNotNone(guard_bash.verdict(data("Get-Content big.log | Select-Object -First 20", "PowerShell")))
        self.assertIsNotNone(guard_bash.verdict(data("Select-String -Path *.cpp -Pattern x", "PowerShell")))
        self.assertIsNone(guard_bash.verdict(data("Get-ChildItem build", "PowerShell")))

    def test_polling_repeat_within_a_minute(self):
        self.assertIsNone(guard_bash.verdict(data("sleep 20", call="p1")))
        self.assertIsNone(guard_bash.verdict(data("sleep 20", call="p1")), "the same call twice is not a poll")
        self.assertIsNotNone(guard_bash.verdict(data("date; tasklist | tail -3", call="p2")))
        self.assertIsNone(guard_bash.verdict(data("sleep 20", agent="other", call="p3")), "agents are separate")
        self.assertIsNone(guard_bash.verdict(data("cmake --build --preset x", call="p4")), "work is never a poll")

    def test_entry_point_fails_open(self):
        script = HERE / "guard_bash.py"
        env = dict(os.environ, DDON_HOOK_LEDGER_DIR=self.tmp.name, DDON_HOOK_POLL_DIR=self.tmp.name)
        bad = subprocess.run([sys.executable, "-X", "utf8", "-I", str(script)], input="not json",
                             capture_output=True, text=True, env=env)
        self.assertEqual(bad.returncode, 0)
        refused = subprocess.run([sys.executable, "-X", "utf8", "-I", str(script)],
                                 input=json.dumps(data("grep x f")), capture_output=True, text=True, env=env)
        self.assertEqual(refused.returncode, 2)
        self.assertIn("rg", refused.stderr)
        rows = (Path(self.tmp.name) / "tool-calls.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(json.loads(rows[-1])["event"], "refused")


if __name__ == "__main__":
    unittest.main()
