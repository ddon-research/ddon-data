"""Tests for agent_cap.py: python -m unittest discover -s tools/hooks"""

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "agent_cap.py"
SPAWN = {"tool_name": "Agent", "tool_input": {"subagent_type": "implementer", "prompt": "x",
                                              "description": "implementer · 002 P4: reconstructor-port wave 2"}}


def spawn(**inp):
    return {"tool_name": "Agent", "tool_input": {**SPAWN["tool_input"], **inp}}


def run(mode, payload, ledger):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK), mode], input=text, capture_output=True,
                          text=True, encoding="utf-8", env=dict(os.environ, DDON_HOOK_LEDGER_DIR=str(ledger)))


class AgentCapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "ledger"
        self.running = self.ledger / "running"

    def tearDown(self):
        self.tmp.cleanup()

    def test_start_then_check_refuses(self):
        self.assertEqual(run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger).returncode, 0)
        record = json.loads((self.running / "a1.json").read_text(encoding="utf-8"))
        self.assertEqual((record["agent_id"], record["agent_type"]), ("a1", "implementer"))
        done = run("check", SPAWN, self.ledger)
        self.assertEqual(done.returncode, 2)
        for part in ("a1", "implementer", "0 min", "one subagent at a time (orchestration section 1)",
                     "resume it with SendMessage"):
            self.assertIn(part, done.stderr)
        refusal = json.loads((self.ledger / "tool-calls.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual((refusal["event"], refusal["hook"]), ("refused", "agent_cap"))

    def test_send_message_is_never_refused(self):
        run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger)
        self.assertEqual(run("check", {"tool_name": "SendMessage", "tool_input": {}}, self.ledger).returncode, 0)

    def test_stop_then_check_allows(self):
        run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger)
        self.assertEqual(run("stop", {"agent_id": "a1", "background_tasks": []}, self.ledger).returncode, 0)
        self.assertFalse((self.running / "a1.json").exists())
        self.assertEqual(run("check", SPAWN, self.ledger).returncode, 0)

    def test_finished_receipt_clears_despite_background_work(self):
        run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger)
        message = "## Receipt P2\n- branch: b   head: 1\n- state: done\n"
        run("stop", {"agent_id": "a1", "background_tasks": 1, "last_assistant_message": message},
            self.ledger)
        self.assertFalse((self.running / "a1.json").exists())
        self.assertEqual(run("check", SPAWN, self.ledger).returncode, 0)

    def test_cut_short_receipt_with_background_work_still_refuses(self):
        run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger)
        message = "## Receipt P2\n- state: cut short: the check.sh summary\n"
        run("stop", {"agent_id": "a1", "background_tasks": 1, "last_assistant_message": message},
            self.ledger)
        result = run("check", SPAWN, self.ledger)
        self.assertEqual(result.returncode, 2)
        self.assertIn(".agent-ledger/running/a1.json", result.stderr)

    def test_receiptless_role_clears_despite_background_work(self):
        run("start", {"agent_id": "a1", "agent_type": "general-purpose"}, self.ledger)
        run("stop", {"agent_id": "a1", "background_tasks": 1}, self.ledger)
        self.assertFalse((self.running / "a1.json").exists())
        self.assertEqual(run("check", SPAWN, self.ledger).returncode, 0)

    def test_stop_with_background_work_still_refuses(self):
        run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger)
        for tasks in ([{"id": "t1"}], 2):
            run("stop", {"agent_id": "a1", "background_tasks": tasks}, self.ledger)
            self.assertTrue((self.running / "a1.json").exists(), tasks)
            self.assertEqual(run("check", SPAWN, self.ledger).returncode, 2, tasks)

    def test_a_stale_file_is_ignored_and_removed(self):
        self.running.mkdir(parents=True)
        old = (dt.datetime.now(dt.UTC) - dt.timedelta(hours=5)).isoformat()
        stale = self.running / "old.json"
        stale.write_text(json.dumps({"agent_id": "old", "agent_type": "implementer", "started": old}), encoding="utf-8")
        junk = self.running / "junk.json"
        junk.write_text("not json", encoding="utf-8")
        past = time.time() - 5 * 3600
        os.utime(junk, (past, past))
        fresh_junk = self.running / "fresh-junk.json"
        fresh_junk.write_text("{}", encoding="utf-8")
        self.assertEqual(run("check", SPAWN, self.ledger).returncode, 0, "stale or unclear records never refuse")
        self.assertFalse(stale.exists())
        self.assertFalse(junk.exists())
        self.assertTrue(fresh_junk.exists(), "an unclear record is deleted only once its mtime is stale")

    def test_age_is_named_in_hours(self):
        self.running.mkdir(parents=True)
        started = (dt.datetime.now(dt.UTC) - dt.timedelta(hours=1, minutes=5)).isoformat()
        (self.running / "a2.json").write_text(json.dumps({"agent_id": "a2", "agent_type": "evidence-researcher",
                                                          "started": started}), encoding="utf-8")
        done = run("check", SPAWN, self.ledger)
        self.assertEqual(done.returncode, 2)
        self.assertIn("a2 (evidence-researcher, running 1 h 5 min)", done.stderr)

    def test_spawn_guard_allows_titled_roles(self):
        # The roles are the real `.claude/agents/*.md` stems.
        for inp in ({},
                    {"subagent_type": "evidence-researcher-ida",
                     "description": "evidence-researcher-ida · 005 P2: rNetMsg lobby handlers"},
                    {"subagent_type": "evidence-researcher-ida",
                     "description": "evidence-researcher · 005 P2: rNetMsg lobby handlers"},
                    {"subagent_type": "general-purpose", "prompt": "Your role is reviewer. Review x.",
                     "description": "reviewer · 002 P5: port review"}):
            self.assertEqual(run("check", spawn(**inp), self.ledger).returncode, 0, inp)

    def test_spawn_guard_refuses_untyped_or_untitled_spawns(self):
        cases = {
            "`subagent_type` is Explore": {"subagent_type": "Explore"},
            "`subagent_type` is missing": {"subagent_type": None},
            "`subagent_type` is general-purpose": {"subagent_type": "general-purpose", "prompt": "Review x.",
                                                   "description": "reviewer · 002 P5: port review"},
            "is not `<role> · <spec> <package>: <what>`": {"description": "Architecture and anti-debug review"},
            "names the role 'reviewer', the agent is a 'implementer'": {
                "description": "reviewer · 002 P4: reconstructor-port wave 2"},
            "which is not a project role": {"subagent_type": "general-purpose", "prompt": "Your role is x.",
                                            "description": "planner · 002 P5: plan"},
        }
        for part, inp in cases.items():
            done = run("check", spawn(**inp), self.ledger)
            self.assertEqual(done.returncode, 2, inp)
            self.assertIn(part, done.stderr)
        no_title = dict(SPAWN["tool_input"])
        del no_title["description"]
        self.assertEqual(run("check", {"tool_name": "Agent", "tool_input": no_title}, self.ledger).returncode, 2)
        refusal = json.loads((self.ledger / "tool-calls.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(refusal["hook"], "agent_cap")

    def test_bad_input_exits_0(self):
        run("start", {"agent_id": "a1", "agent_type": "implementer"}, self.ledger)
        for mode in ("start", "stop", "check", "bogus"):
            for text in ("", "not json", "[1]"):
                self.assertEqual(run(mode, text, self.ledger).returncode, 0, (mode, text))
        self.assertTrue((self.running / "a1.json").exists(), "a bad stop input removes nothing")
        self.assertEqual(sorted(p.name for p in self.running.iterdir()), ["a1.json"])


if __name__ == "__main__":
    unittest.main()
