"""SubagentStop hook: records each stop of a subagent; never blocks.

Ported from the reconstructor's `tools/hooks/subagent_stop.py` (no worktree logic: ddon-data has
one checkout).
- Appends one row to `.agent-ledger/stops.jsonl`: the time, the agent's id and type, the message's
  length in characters and in non-blank lines, its first line's prefix (`waiting:`, `blocked:` or
  none), the count of `background_tasks` the hook input names, and `stop_hook_active` (a stop
  after a refusal).
- Keeps the full message in `.agent-ledger/reports/<agent id>.md`, the latest stop's, so the
  coordinator reads a report from the file, not from its context.

The agent id is the input's `agent_id`, else the `agent-<id>` stem of its transcript path, else
`unknown`. `DDON_HOOK_LEDGER_DIR` (for the tests) replaces `.agent-ledger/`. Any failure prints one
line to stderr and exits 0.
"""

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

PREFIXES = ("waiting:", "blocked:")
SAFE = re.compile(r"[^A-Za-z0-9_.-]")


def agent_of(data):
    agent = data.get("agent_id")
    if isinstance(agent, str) and agent.strip():
        return SAFE.sub("_", agent.strip())
    for key in ("agent_transcript_path", "transcript_path"):
        stem = Path(str(data.get(key) or "")).stem
        if stem.startswith("agent-"):
            return SAFE.sub("_", stem.removeprefix("agent-"))
    return "unknown"


def count(value):
    """`background_tasks` as a number: a list's or a mapping's length, an integer itself."""
    if isinstance(value, (list, dict)):
        return len(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return max(value, 0)
    return 0


def record(data, out):
    message = data.get("last_assistant_message")
    message = message if isinstance(message, str) else ""
    lines = [line for line in message.splitlines() if line.strip()]
    first = lines[0].lstrip() if lines else ""
    agent = agent_of(data)
    row = {"time": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"), "agent_id": agent,
           "agent_type": data.get("agent_type"), "chars": len(message), "lines": len(lines),
           "prefix": next((p for p in PREFIXES if first.startswith(p)), None),
           "background_tasks": count(data.get("background_tasks")),
           "stop_hook_active": bool(data.get("stop_hook_active"))}
    (out / "reports").mkdir(parents=True, exist_ok=True)
    with (out / "stops.jsonl").open("a", encoding="utf-8", newline="\n") as stops:
        stops.write(json.dumps(row) + "\n")
    (out / "reports" / f"{agent}.md").write_text(message, encoding="utf-8", newline="\n")
    return row


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if not isinstance(data, dict):
            raise ValueError("the hook input is not an object")
        record(data, hooklib.ledger_dir())
    except Exception as error:  # noqa: BLE001 (a record never blocks a stop)
        print(f"subagent_stop: not recorded: {type(error).__name__}: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
