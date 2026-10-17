"""Subagent cap: at most one subagent of any role runs at a time (orchestration section 1).

One script, one mode per hook event (the first argument):
- `start` (SubagentStart): writes `.agent-ledger/running/<agent id>.json` with
  `{agent_id, agent_type, started}`.
- `stop` (SubagentStop): removes that file, unless the input names background work
  (`background_tasks` > 0, read as `subagent_stop.py` reads it) and the final message is not a
  finished receipt (a `- state: done` line): such an agent will resume, so it still counts as
  running. A finished receipt clears the record even with background work left, because an agent
  that reports done while its last build finishes may never stop again (ddon-hook, 2026-10-17: a
  landed agent's record blocked the next spawn).
- `check` (PreToolUse on `Agent`): refuses (exit 2, message on stderr) while a running record
  younger than 4 h exists, naming the agent, its type and its age. Records older than 4 h are stale:
  ignored and deleted. `SendMessage` (resuming an agent) is never refused.

Unparseable input exits 0 in every mode (a hook bug never blocks work), and `check` refuses only on
a clear running record: a JSON object with an agent id and a parseable `started` time. Files that
are not such a record are ignored, and deleted once their mtime is older than 4 h.
`DDON_HOOK_LEDGER_DIR` (for the tests) replaces `.agent-ledger/`.
"""

import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402
from subagent_stop import agent_of, count  # noqa: E402

STALE_SECONDS = 4 * 3600
FINISHED = re.compile(r"^- state: done\b", re.MULTILINE)
RULE = "one subagent at a time (orchestration section 1): land or stop it first, or resume it with SendMessage"


def running_dir():
    return hooklib.ledger_dir() / "running"


def start(data):
    agent = agent_of(data)
    if agent == "unknown":
        return 0
    directory = running_dir()
    directory.mkdir(parents=True, exist_ok=True)
    record = {"agent_id": agent, "agent_type": data.get("agent_type"), "started": hooklib.now_iso()}
    temp = directory / f".{agent}.tmp"
    temp.write_text(json.dumps(record) + "\n", encoding="utf-8", newline="\n")
    temp.replace(directory / f"{agent}.json")
    return 0


def finished(data):
    message = data.get("last_assistant_message")
    return isinstance(message, str) and FINISHED.search(message) is not None


def stop(data):
    if count(data.get("background_tasks")) > 0 and not finished(data):
        return 0
    agent = agent_of(data)
    if agent != "unknown":
        (running_dir() / f"{agent}.json").unlink(missing_ok=True)
    return 0


def age_of(record):
    """Seconds since the record's `started`, or None when it is not a clear running record."""
    if not isinstance(record, dict) or not isinstance(record.get("agent_id"), str):
        return None
    try:
        started = dt.datetime.fromisoformat(str(record.get("started")))
    except ValueError:
        return None
    if started.tzinfo is None:
        return None
    return (dt.datetime.now(dt.UTC) - started).total_seconds()


def human(seconds):
    minutes = int(max(seconds, 0) // 60)
    return f"{minutes // 60} h {minutes % 60} min" if minutes >= 60 else f"{minutes} min"


def live_records():
    """The clear, fresh running records; stale files are deleted on the way."""
    live = []
    directory = running_dir()
    if not directory.is_dir():
        return live
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            record = None
        age = age_of(record)
        try:
            if age is None:
                if time.time() - path.stat().st_mtime > STALE_SECONDS:
                    path.unlink(missing_ok=True)
                continue
            if age > STALE_SECONDS:
                path.unlink(missing_ok=True)
                continue
        except OSError:
            continue
        live.append((record, age))
    return live


def check(data):
    if data.get("tool_name") == "SendMessage":
        return 0
    live = live_records()
    if not live:
        return 0
    names = "; ".join(f"{r['agent_id']} ({r.get('agent_type') or 'unknown type'}, running {human(age)})"
                      for r, age in live)
    files = ", ".join(f".agent-ledger/running/{r['agent_id']}.json" for r, _ in live)
    reason = (f"Refused: a subagent is running: {names}. {RULE}. If it has in fact finished "
              f"(its receipt says done), delete {files} and spawn again.")
    hooklib.record_refusal(data, "agent_cap", reason)
    print(reason, file=sys.stderr)
    return 2


MODES = {"start": start, "stop": stop, "check": check}


def main():
    mode = MODES.get(sys.argv[1] if len(sys.argv) > 1 else "")
    data = hooklib.read_input()
    if mode is None or data is None:
        return 0
    return mode(data)


if __name__ == "__main__":
    hooklib.fail_open(main)
