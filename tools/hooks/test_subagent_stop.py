"""Tests for subagent_stop.py: python -m unittest discover -s tools/hooks"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "subagent_stop.py"


def run(payload, ledger):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=text, capture_output=True, text=True,
                          encoding="utf-8", env=dict(os.environ, DDON_HOOK_LEDGER_DIR=str(ledger)))


class SubagentStopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "ledger"

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self):
        path = self.ledger / "stops.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.is_file() else []

    def test_a_stop_is_recorded_and_its_report_kept(self):
        final = "P9 done.\nReceipt below.\n\n## Receipt P9"
        done = run({"agent_id": "a1b2", "agent_type": "implementer", "last_assistant_message": final,
                    "background_tasks": [{"id": "t1"}, {"id": "t2"}]}, self.ledger)
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        row = self.rows()[-1]
        self.assertEqual((row["agent_id"], row["agent_type"], row["chars"], row["lines"], row["background_tasks"],
                          row["prefix"], row["stop_hook_active"]), ("a1b2", "implementer", len(final), 3, 2, None, False))
        report = self.ledger / "reports" / "a1b2.md"
        self.assertEqual(report.read_text(encoding="utf-8"), final)
        run({"agent_id": "a1b2", "last_assistant_message": "waiting: the go", "stop_hook_active": True}, self.ledger)
        row = self.rows()[-1]
        self.assertEqual((row["prefix"], row["stop_hook_active"], len(self.rows())), ("waiting:", True, 2))
        self.assertEqual(report.read_text(encoding="utf-8"), "waiting: the go", "the latest stop's message is kept")

    def test_id_from_the_transcript_and_a_numeric_task_count(self):
        run({"transcript_path": "C:/t/subagents/agent-ffee.jsonl", "last_assistant_message": "blocked:signing",
             "background_tasks": 3}, self.ledger)
        row = self.rows()[-1]
        self.assertEqual((row["agent_id"], row["background_tasks"], row["prefix"]), ("ffee", 3, "blocked:"))
        run({"last_assistant_message": "x"}, self.ledger)
        self.assertEqual(self.rows()[-1]["agent_id"], "unknown")

    def test_an_id_cannot_leave_reports(self):
        run({"agent_id": "../../evil", "last_assistant_message": "x"}, self.ledger)
        self.assertEqual(self.rows()[-1]["agent_id"], ".._.._evil")
        self.assertTrue((self.ledger / "reports" / ".._.._evil.md").is_file())
        self.assertFalse((Path(self.tmp.name).parent / "evil.md").exists())

    def test_bad_input_exits_0(self):
        for text in ("", "not json", "[1]"):
            done = run(text, self.ledger)
            self.assertEqual(done.returncode, 0, text)
        self.assertEqual(len(self.rows()), 1, "empty stdin is an empty object: one row, agent unknown")


if __name__ == "__main__":
    unittest.main()
