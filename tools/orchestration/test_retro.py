"""Tests for retro.py: python -m unittest discover -s tools/orchestration"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import retro  # noqa: E402


def assistant(mid, stamp, context, output=10):
    usage = {"input_tokens": 2, "cache_creation_input_tokens": 98, "cache_read_input_tokens": context - 100,
             "output_tokens": output}
    return json.dumps({"type": "assistant", "timestamp": stamp, "message": {"id": mid, "model": "m", "usage": usage}})


class RetroTest(unittest.TestCase):
    def test_report_and_ledger_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "tool-calls.jsonl"
            rows = [
                {"at": "2026-10-17T10:00:00+02:00", "event": "call", "tool": "Bash", "cmd": "date", "agent": "a",
                 "response_chars": 4000, "duration_ms": 50},
                {"at": "2026-10-17T10:00:30+02:00", "event": "call", "tool": "Bash", "cmd": "date", "agent": "a",
                 "response_chars": 40},
                {"at": "2026-10-17T10:01:00+02:00", "event": "call", "tool": "Bash", "cmd": "date", "agent": "a"},
                {"at": "2026-10-17T10:02:00+02:00", "event": "failed", "tool": "Read", "error": "missing"},
                {"at": "2026-10-17T10:03:00+02:00", "event": "refused", "hook": "guard_bash", "reason": "grep"},
                {"at": "2026-10-16T10:00:00+02:00", "event": "call", "tool": "Bash", "cmd": "old"},
            ]
            ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
            projects = root / "projects"
            (projects / "s1" / "subagents").mkdir(parents=True)
            (projects / "s1.jsonl").write_text("\n".join([
                assistant("m1", "2026-10-17T08:00:00Z", 50_000),
                assistant("m1", "2026-10-17T08:00:01Z", 50_000, output=50),  # the same response again, final count
                assistant("m2", "2026-10-17T08:05:00Z", 80_000)]) + "\n", encoding="utf-8")
            agent = projects / "s1" / "subagents" / "agent-x.jsonl"
            agent.write_text(assistant("m3", "2026-10-17T08:00:00Z", 30_000) + "\n"
                             + assistant("m4", "2026-10-17T09:00:00Z", 40_000) + "\n", encoding="utf-8")
            agent.with_name("agent-x.meta.json").write_text(json.dumps({"agentType": "implementer", "description": "P1"}),
                                                            encoding="utf-8")
            history = root / "history.jsonl"
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                retro.main(["--since", "2026-10-17", "--label", "t", "--ledger", str(ledger), "--transcripts",
                            str(projects), "--history", str(history), "--append"])
            text = out.getvalue()
            self.assertIn("3 x [a] `date`", text)
            self.assertIn("implementer: P1", text)
            self.assertIn("guard_bash: grep", text)
            m = json.loads(history.read_text(encoding="utf-8"))["metrics"]
            self.assertEqual(m["calls"], 4)
            self.assertEqual((m["sessions"], m["subagents"], m["turns"]), (1, 1, 4))
            self.assertEqual(m["main_peak_context"], 80_000)
            self.assertEqual(m["tokens_output"], 80, "the last usage of a response wins")
            self.assertEqual(m["agent_hours"], 1.0)
            self.assertEqual(m["refused_pct"], 20.0)


if __name__ == "__main__":
    unittest.main()
