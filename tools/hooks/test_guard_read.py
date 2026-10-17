"""Tests for guard_read.py: python -m unittest discover -s tools/hooks"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard_read  # noqa: E402


def read(path, agent="a", **extra):
    return {"tool_name": "Read", "session_id": "s", "agent_id": agent,
            "tool_input": {"file_path": str(path), **extra}}


class GuardReadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.env = mock.patch.dict(os.environ, {"DDON_HOOK_READ_DIR": str(root / "state")})
        self.env.start()
        self.big = root / "big.log"
        self.big.write_text("x" * (guard_read.SIZE + 1), encoding="utf-8")
        self.small = root / "small.cpp"
        self.small.write_text("int x;\n", encoding="utf-8")
        self.notes = root / "tasks.md"
        self.notes.write_text("y" * (guard_read.MARKDOWN_SIZE + 1), encoding="utf-8")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_first_whole_read_of_a_big_file_is_refused_once(self):
        self.assertIsNotNone(guard_read.verdict(read(self.big)))
        self.assertIsNone(guard_read.verdict(read(self.big)), "the second whole read runs")
        self.assertIsNotNone(guard_read.verdict(read(self.big, agent="other")), "per agent")

    def test_markdown_has_a_lower_threshold(self):
        self.assertIsNotNone(guard_read.verdict(read(self.notes)))

    def test_partial_small_missing_and_images_pass(self):
        self.assertIsNone(guard_read.verdict(read(self.big, agent="p", offset=10, limit=50)))
        self.assertIsNone(guard_read.verdict(read(self.small)))
        self.assertIsNone(guard_read.verdict(read(Path(self.tmp.name) / "missing.txt")))
        image = Path(self.tmp.name) / "shot.png"
        image.write_bytes(b"\0" * (guard_read.SIZE + 1))
        self.assertIsNone(guard_read.verdict(read(image)))


if __name__ == "__main__":
    unittest.main()
