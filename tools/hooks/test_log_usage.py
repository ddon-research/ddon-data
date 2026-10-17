"""Tests for log_usage.py: python -m unittest discover -s tools/hooks"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "log_usage.py"
USAGE = {"plan": {"windows": [{"label": "Weekly · all models", "percentUsed": 41, "resetsAt": "2026-10-20T00:00:00Z"},
                              {"label": "5-hour limit", "percentUsed": 7}]}}


def run(text, ledger):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=text, capture_output=True, text=True,
                          encoding="utf-8", env=dict(os.environ, DDON_HOOK_LEDGER_DIR=str(ledger)))


class LogUsageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name)
        self.log = self.ledger / "usage-readings.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self):
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()] if self.log.exists() else []

    def test_every_response_shape(self):
        shapes = [USAGE, json.dumps(USAGE), {"content": [{"type": "text", "text": json.dumps(USAGE)}]},
                  [{"type": "text", "text": json.dumps(USAGE)}]]
        for shape in shapes:
            done = run(json.dumps({"tool_name": "mcp__ccd_session_mgmt__get_usage", "tool_response": shape}), self.ledger)
            self.assertEqual((done.returncode, done.stdout), (0, ""))
        rows = self.rows()
        self.assertEqual(len(rows), 4)
        self.assertEqual({k: rows[0][k] for k in ("weekly", "weekly_resets_at", "five_hour")},
                         {"weekly": 41, "weekly_resets_at": "2026-10-20T00:00:00Z", "five_hour": 7})
        self.assertEqual(sorted(rows[0]), ["at", "five_hour", "weekly", "weekly_resets_at"])

    def test_bad_input_exits_0_and_writes_nothing(self):
        for text in ("", "not json", "[]", json.dumps({"tool_response": "not json"}),
                     json.dumps({"tool_response": {"plan": {"windows": [{"label": "5-hour limit", "percentUsed": 1}]}}}),
                     json.dumps({"tool_response": {"plan": {"windows": "x"}}})):
            done = run(text, self.ledger)
            self.assertEqual((done.returncode, done.stdout), (0, ""), text)
        self.assertEqual(self.rows(), [])


if __name__ == "__main__":
    unittest.main()
