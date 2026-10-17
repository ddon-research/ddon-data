"""Tests for receipt.py against a throwaway git repository: python -m unittest discover -s tools/hooks"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import receipt  # noqa: E402


def git(cwd, *args):
    # A throwaway repository: unsigned commits are fine here and let the test see code `N`.
    return subprocess.run(["git", "-C", str(cwd), "-c", "commit.gpgsign=false", "-c", "user.name=t",
                           "-c", "user.email=t@example.invalid", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


class ReceiptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        git(cls.repo, "init", "-q", "-b", "pkg")
        (cls.repo / "a.txt").write_text("a\n", encoding="utf-8")
        git(cls.repo, "add", "a.txt")
        git(cls.repo, "commit", "-q", "-m", "Base")
        cls.base = git(cls.repo, "rev-parse", "HEAD")
        (cls.repo / "b.txt").write_text("b\n", encoding="utf-8")
        git(cls.repo, "add", "b.txt")
        git(cls.repo, "commit", "-q", "-m", "Add b")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def message(self):
        ident = receipt.identity(self.repo, self.base)
        text = receipt.render("P1", ident).replace("<command: result, one per gate>", "ctest 140/140")
        return "Done.\n\n" + text, ident

    def test_render_parses_back(self):
        text, ident = self.message()
        claimed = receipt.parse(text)
        self.assertEqual(claimed["branch"], "pkg")
        self.assertEqual(len(claimed["commits"]), 1)
        found = receipt.problems(claimed, ident)
        self.assertEqual(found, [f"unsigned or badly signed commits: {ident['head'][:10]} (stop and report blocked:signing)"])

    def test_mismatches_are_found(self):
        text, ident = self.message()
        ident = {**ident, "signatures": ["G"]}
        self.assertEqual(receipt.problems(receipt.parse(text), ident), [])
        wrong = text.replace("branch: pkg", "branch: other").replace("ctest 140/140", "<command: result>")
        found = receipt.problems(receipt.parse(wrong), ident)
        self.assertTrue(any(f.startswith("branch:") for f in found))
        self.assertTrue(any(f.startswith("gates:") for f in found))
        dropped = "\n".join(line for line in text.splitlines() if not line.startswith("  - "))
        self.assertTrue(any(f.startswith("commits:") for f in receipt.problems(receipt.parse(dropped), ident)))

    def test_status_covers_only_the_committed_files(self):
        # ddon-data: the shared checkout holds other work, so only the package's own files count.
        other = self.repo / "other.txt"
        other.write_text("someone else's work\n", encoding="utf-8")
        try:
            self.assertEqual(receipt.identity(self.repo, self.base)["status"], [])
            (self.repo / "b.txt").write_text("b changed after the commit\n", encoding="utf-8")
            status = receipt.identity(self.repo, self.base)["status"]
            self.assertEqual(len(status), 1)
            self.assertTrue(status[0].endswith("b.txt"))
        finally:
            other.unlink()
            (self.repo / "b.txt").write_text("b\n", encoding="utf-8")

    def test_stop_hook(self):
        script = HERE / "receipt.py"

        def stop(data):
            return subprocess.run([sys.executable, "-X", "utf8", "-I", str(script), "--check"],
                                  input=json.dumps(data), capture_output=True, text=True)

        missing = stop({"cwd": str(self.repo), "last_assistant_message": "All done."})
        self.assertEqual(missing.returncode, 2)
        self.assertIn(receipt.REFUSED, missing.stderr)
        text, _ = self.message()
        unsigned = stop({"cwd": str(self.repo), "last_assistant_message": text})
        self.assertEqual(unsigned.returncode, 2, "the throwaway commit is unsigned")
        self.assertEqual(stop({"cwd": str(self.repo), "last_assistant_message": "x", "stop_hook_active": True}).returncode, 0)
        self.assertEqual(stop({"cwd": str(self.repo)}).returncode, 0, "no message: fail open")


if __name__ == "__main__":
    unittest.main()
