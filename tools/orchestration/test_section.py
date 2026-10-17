"""Tests for section.py: python -m unittest discover -s tools/orchestration"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "section.py"
DOC = "# Top\nintro\n## Alpha\na1\n```\n# not a heading\n```\n### Alpha detail\na2\n## Beta\nb1\n"


def run(*args):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *args], capture_output=True, text=True,
                          encoding="utf-8")


class SectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.doc = Path(self.tmp.name) / "doc.md"
        self.doc.write_text(DOC, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_section_with_its_subsections(self):
        done = run(str(self.doc), "alpha")
        self.assertEqual(done.returncode, 0)
        self.assertIn("lines 3-9", done.stdout)
        self.assertIn("a2", done.stdout)
        self.assertNotIn("b1", done.stdout)

    def test_list_skips_fenced_lines(self):
        done = run(str(self.doc), "--list")
        self.assertNotIn("not a heading", done.stdout)
        self.assertIn("Alpha detail", done.stdout)

    def test_missing_heading_and_usage(self):
        self.assertEqual(run(str(self.doc), "gamma").returncode, 1)
        self.assertEqual(run(str(self.doc)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
