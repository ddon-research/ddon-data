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
    "git push origin main 2>&1 | tail -2",
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
    # 009 T003: only the small subtrees of packets/ are exempt, under every spelling
    "tree packets/",
    "fd -e json . ./packets",
    "rg -n x packets/decrypted_json",
    "rg -n x ./packets/decrypted_raw",
    "rg -n x packets/encrypted_streams",
    "rg -n x /d/ddon-data/packets/decrypted_annotated",
    "git diff -- packets",
    "git diff -- packets/patterns packets/decrypted_json",
    "rg -n x packets/patterns/../decrypted_json",
    "rg -n x ./packets/patterns/../decrypted_json",
    "rg -n x D:/ddon-data/packets/patterns/../decrypted_json",
    "rg -n x /d/ddon-data/packets/tools/../../packets/decrypted_raw",
    "git diff -- packets/tests/../decrypted_json",
    "fd -e json . packets/plbatch/../encrypted_streams",
    "rg -n x packets/patterns-old",
    "rg -n x packets/patterns/../../client/03040008",
    "git checkout -- packets/patterns/",
    "git restore packets/patterns/",
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
    "git push origin rng-monitor 2>&1 | tail -2",
    "git push origin rng-monitor 2>/dev/null > log.txt",
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
    # 009 T003: the small subtrees of packets/, in every spelling
    "rg -n x packets/patterns",
    "rg -n x packets/patterns/03040008/include",
    "rg -n x ./packets/tools",
    "rg -n x packets/tests/",
    "rg -n x D:/ddon-data/packets/plbatch",
    "rg -n x /d/ddon-data/packets/wireshark",
    "rg -n x packets/patterns/../tools",
    "fd -e cpp . packets/patterns",
    "fd . ./packets/plbatch",
    "ls -R packets/tools",
    "tree packets/wireshark",
    "git ls-files packets/patterns",
    "git diff -- packets/patterns/03040008/include",
    "git diff -- ./packets/tools packets/imhex-export.sh",
    "git checkout -- packets/patterns/03040008/C2L_PING_REQ-pattern.cpp",
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
        self.staged = mock.patch.object(guard_bash, "staged_paths", return_value=(Path(".").resolve(), []))
        self.staged.start()

    def tearDown(self):
        self.staged.stop()
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

    def test_push_checks_the_branch_of_the_repository_it_runs_in(self):
        def branch_of(directory):
            return "main" if Path(directory).name == "sibling" else "rng-monitor"
        with mock.patch.object(guard_bash, "current_branch", side_effect=branch_of):
            for index, command in enumerate(("cd /d/sibling && git push origin main",
                                             "cd /d/sibling; git push origin main",
                                             "git -C /d/sibling push origin main",
                                             "cd /d/other && git -C /d/sibling push origin main",
                                             "git push origin rng-monitor")):
                with self.subTest(command=command):
                    self.assertIsNone(guard_bash.verdict(data(command, agent=f"s{index}", call=f"s{index}")))
            for index, command in enumerate(("git push origin main",
                                             "cd /d/other && git push origin main",
                                             "cd /d/sibling && git push origin rng-monitor",
                                             "cd /d/sibling && git push --force origin main",
                                             "cd /d/sibling && git push origin :main",
                                             'cd "$S" && git push origin main',
                                             "cd - && git push origin main")):
                with self.subTest(command=command):
                    self.assertIsNotNone(guard_bash.verdict(data(command, agent=f"t{index}", call=f"t{index}")))

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
            # T020: owned folders after `--`, a handful at most; never the checkout, a parent or a glob.
            for i in range(6):
                (Path(root) / "d" / str(i)).mkdir(parents=True)
            self.assertIsNone(check("git add -- specs/011 d/0"))
            self.assertIsNone(check("git add -u -- d/0"))
            self.assertIsNotNone(check("git add -- d/0 d/1 d/2 d/3 d/4 d/5"))
            self.assertIsNotNone(check("git add -- d/.."))
            self.assertIsNotNone(check("git add -- specs/.."))
            self.assertIsNotNone(check("git add -- d/*"))
            self.assertIsNotNone(check("git add -- ."))
            self.assertIsNotNone(check("git add -A -- d/0"))
            self.assertIsNotNone(check("git add -u"))
            for command in ("git add --pathspec-from-file=list.txt", "git add --pathspec-from-file list.txt",
                            "git commit -m x --pathspec-from-file=list.txt"):
                self.assertIn("update-index", check(command))

    def test_bare_commit_with_other_staged_paths(self):
        # T017: a commit without `-- <paths>` takes the whole index, other sessions' staged files included.
        root = Path(self.tmp.name).resolve()
        cwd = str(root)
        others = (root, ["research/external/flag-smasher.csx", "tools/hooks/a.py"])
        own = (root, ["tools/hooks/a.py", "tools/hooks/sub/b.py"])

        def verdict(command, staged):
            with mock.patch.object(guard_bash, "staged_paths", return_value=staged):
                return guard_bash.verdict({**data(command, call=command), "cwd": cwd})

        reason = verdict("git add tools/hooks/a.py && git commit -m x", others)
        self.assertIn("flag-smasher.csx", reason)
        self.assertIn("-- <your paths", reason)
        self.assertIsNotNone(verdict("git commit -m x", own))
        self.assertIsNotNone(verdict("git commit -i -m x -- tools/hooks/a.py", others))
        self.assertIsNotNone(verdict("git commit -m x", None))
        self.assertIsNone(verdict("git add -- tools/hooks/a.py tools/hooks/sub && git commit -m x", own))
        self.assertIsNone(verdict("git commit -m x -- tools/hooks/a.py", others))
        self.assertIsNone(verdict("git commit -m x", (root, [])))

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
