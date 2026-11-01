"""Tests for log_tool.py and context_watch.py: python -m unittest discover -s tools/hooks"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script, data, ledger):
    env = dict(os.environ, DDON_HOOK_LEDGER_DIR=str(ledger))
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(HERE / script)], input=json.dumps(data),
                          capture_output=True, text=True, env=env)


def rows(ledger):
    return [json.loads(line) for line in (ledger / "tool-calls.jsonl").read_text(encoding="utf-8").splitlines()]


class LogToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_pre_then_post_records_duration(self):
        base = {"tool_name": "Bash", "tool_use_id": "toolu_1", "session_id": "s",
                "tool_input": {"command": "cmake --build --preset x86-debug-vs2026"}}
        self.assertEqual(run("log_tool.py", {**base, "hook_event_name": "PreToolUse"}, self.ledger).returncode, 0)
        post = {**base, "hook_event_name": "PostToolUse", "tool_response": {"stdout": "ok", "stderr": ""}}
        self.assertEqual(run("log_tool.py", post, self.ledger).returncode, 0)
        row = rows(self.ledger)[-1]
        self.assertEqual((row["event"], row["tool"], row["ok"]), ("call", "Bash", True))
        self.assertIn("duration_ms", row)
        self.assertTrue(row["cmd"].startswith("cmake --build"))
        self.assertFalse((self.ledger / "inflight" / "toolu_1").exists())

    def test_failure_and_harness_duration(self):
        data = {"hook_event_name": "PostToolUseFailure", "tool_name": "Read", "tool_use_id": "t2",
                "tool_input": {"file_path": "C:/x"}, "error": "File does not exist", "duration_ms": 12}
        run("log_tool.py", data, self.ledger)
        row = rows(self.ledger)[-1]
        self.assertEqual((row["event"], row["ok"], row["duration_ms"]), ("failed", False, 12))
        self.assertIn("does not exist", row["error"])

    def test_bad_input_exits_zero(self):
        env = dict(os.environ, DDON_HOOK_LEDGER_DIR=str(self.ledger))
        bad = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HERE / "log_tool.py")], input="{",
                             capture_output=True, text=True, env=env)
        self.assertEqual(bad.returncode, 0)


def response(tokens):
    usage = {"input_tokens": 2, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": tokens - 1002}
    return json.dumps({"type": "assistant", "message": {"role": "assistant", "usage": usage}})


class ContextWatchTest(unittest.TestCase):
    def test_reminds_once_per_threshold_and_skips_subagents(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger, transcript = Path(tmp), Path(tmp, "session.jsonl")
            transcript.write_text(response(100_000) + "\n" + response(440_000) + "\n", encoding="utf-8")
            data = {"transcript_path": str(transcript), "hook_event_name": "PostToolUse", "tool_name": "Bash"}
            self.assertEqual(run("context_watch.py", data, ledger).stdout.strip(), "", "below 450k: quiet")
            with open(transcript, "a", encoding="utf-8") as handle:
                handle.write(response(460_000) + "\n")
            first = run("context_watch.py", data, ledger)
            self.assertIn("460k", first.stdout)
            self.assertIn("next natural break", first.stdout)
            self.assertEqual(json.loads(first.stdout)["hookSpecificOutput"]["hookEventName"], "PostToolUse")
            self.assertEqual(run("context_watch.py", data, ledger).stdout.strip(), "")
            self.assertEqual(run("context_watch.py", {**data, "agent_id": "a"}, ledger).stdout.strip(), "")
            with open(transcript, "a", encoding="utf-8") as handle:
                handle.write(response(510_000) + "\n")
            late = run("context_watch.py", data, ledger).stdout
            self.assertIn("Commit the records at this break", late)
            self.assertIn("550k", late)
            for text in (first.stdout, late):
                self.assertNotIn("run /compact", text, "never ask the user for /compact")


if __name__ == "__main__":
    unittest.main()
