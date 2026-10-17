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


def assistant(mid, stamp, context, output=10, model="m"):
    usage = {"input_tokens": 2, "cache_creation_input_tokens": 98, "cache_read_input_tokens": context - 100,
             "output_tokens": output}
    return json.dumps({"type": "assistant", "timestamp": stamp, "message": {"id": mid, "model": model, "usage": usage}})


def prompt(text, stamp="2026-10-17T08:00:00Z"):
    return json.dumps({"type": "user", "timestamp": stamp, "message": {"role": "user", "content": text}})


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
            row = json.loads(history.read_text(encoding="utf-8"))
            self.assertIn("head", row)
            self.assertIn("m (4 responses)", row["unavailable"]["cost.unpriced_models"])


class CostTest(unittest.TestCase):
    def test_cost_of_one_response(self):
        usage = {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000,
                 "cache_creation_input_tokens": 3_000_000,
                 "cache_creation": {"ephemeral_5m_input_tokens": 1_000_000, "ephemeral_1h_input_tokens": 2_000_000}}
        # 4 in + 20 out + 0.20 read + 1.25 * 4 (5 min) + 2 * 2 * 4 (1 h)
        self.assertAlmostEqual(retro.cost("claude-opus-5-5", usage), 4 + 20 + 0.2 + 5 + 16)
        self.assertAlmostEqual(retro.cost("claude-opus-5-5[1m]", usage), retro.cost("claude-opus-5-5", usage))
        fast = dict(usage, speed="fast")
        self.assertAlmostEqual(retro.cost("claude-opus-5-5", fast), 8 + 40 + 0.2 + 5 + 16)

    def test_an_unknown_model_is_never_priced(self):
        self.assertIsNone(retro.cost("claude-unknown-9", {"input_tokens": 10}))


class ExtendedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write_repo(self):
        repo = self.root / "repo"
        (repo / ".claude" / "agents").mkdir(parents=True)
        (repo / "specs" / "x" / "briefs").mkdir(parents=True)
        (repo / "AGENTS.md").write_text("a" * 400, encoding="utf-8")
        (repo / ".claude" / "agents" / "implementer.md").write_text("b" * 80, encoding="utf-8")
        (repo / "specs" / "x" / "briefs" / "P1.md").write_text("Build it.\nStop: budget 30 min.\n", encoding="utf-8")
        return repo

    def records(self, repo):
        projects = self.root / "projects"
        (projects / "s1" / "subagents").mkdir(parents=True)
        (projects / "s1.jsonl").write_text(
            assistant("c1", "2026-10-17T08:00:00Z", 1_000_000, output=0, model="claude-opus-5-5") + "\n", encoding="utf-8")
        agents = projects / "s1" / "subagents"
        brief = str(repo / "specs" / "x" / "briefs" / "P1.md").replace("/", "\\")
        # 70 minutes against a 30-minute brief: over 1x and 2x
        (agents / "agent-a.jsonl").write_text("\n".join([
            prompt(f"Your brief is {brief}: read it first."),
            assistant("a1", "2026-10-17T08:00:00Z", 1_000_000, output=0, model="claude-opus-5-5"),
            assistant("a2", "2026-10-17T09:10:00Z", 1_000_000, output=0, model="claude-opus-5-5")]) + "\n",
            encoding="utf-8")
        # an inline budget in the prompt, 10 minutes of 1 h: within it
        (agents / "agent-b.jsonl").write_text("\n".join([
            prompt("Review this. Budget: 1 h."),
            assistant("b1", "2026-10-17T08:00:00Z", 1_000_000, output=0, model="claude-sonnet-5-5"),
            assistant("b2", "2026-10-17T08:10:00Z", 1_000, output=0, model="claude-unknown-9")]) + "\n", encoding="utf-8")
        # no budget anywhere
        (agents / "agent-c.jsonl").write_text(prompt("Look around.") + "\n"
                                              + assistant("c9", "2026-10-17T08:00:00Z", 1_000_000, output=0,
                                                          model="claude-opus-5-5") + "\n", encoding="utf-8")
        return retro.transcripts(projects, retro.moment("2026-10-17"), None)

    def test_cost_budget_and_instruction_metrics(self):
        repo = self.write_repo()
        m, unavailable = retro.extended(self.records(repo), repo)
        # each 1M-token response: 2 in, 98 5-minute writes, the rest cache reads
        opus = retro.cost("claude-opus-5-5", {"input_tokens": 2, "cache_creation_input_tokens": 98,
                                              "cache_read_input_tokens": 999_900})
        sonnet = retro.cost("claude-sonnet-5-5", {"input_tokens": 2, "cache_creation_input_tokens": 98,
                                                  "cache_read_input_tokens": 999_900})
        self.assertAlmostEqual(m["cost.total_usd"], round(4 * opus + sonnet, 2))
        self.assertAlmostEqual(m["cost.coordinator_usd"], round(opus, 2))
        self.assertAlmostEqual(m["cost.coordinator_share_pct"], round(100 * opus / (4 * opus + sonnet), 1))
        self.assertEqual(len(m["cost.per_agent_usd"]), 3)
        self.assertIn("claude-unknown-9 (1 responses)", unavailable["cost.unpriced_models"])
        self.assertEqual((m["waste.budget_overruns_1x"], m["waste.budget_overruns_2x"]), (1, 1))
        self.assertIn("1 agents without a budget", unavailable["waste.budget_unknown"])
        self.assertEqual(m["instructions.agents_md_tokens"], 100)
        self.assertEqual(m["instructions.roles_tokens"], 20)
        self.assertIn("instructions.claude_md_tokens", unavailable)
        self.assertIn("instructions.skill_tokens", unavailable)

    def test_no_budget_at_all_is_unavailable(self):
        record = {"kind": "subagent", "name": "x", "id": "agent-x", "usd": 0.0, "unpriced": {}, "prompt": "go",
                  "first": "2026-10-17T08:00:00Z", "last": "2026-10-17T10:00:00Z"}
        m, unavailable = retro.extended([record], self.root)
        self.assertNotIn("waste.budget_overruns_1x", m)
        self.assertIn("waste.budget_overruns_2x", unavailable)
        self.assertIn("cost.coordinator_share_pct", unavailable)

    def test_budget_forms(self):
        for text, minutes in (("Stop: budget 90 min.", 90), ("Budget: 1.5 h", 90), ("budget 45 minutes", 45),
                              ("`Budget:`/`budget <N> min` line", None)):
            self.assertEqual(retro.budget_minutes({"prompt": text}, self.root), minutes, text)


if __name__ == "__main__":
    unittest.main()
