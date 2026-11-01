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
  Only the roles in RECEIPT_ROLES end with a receipt; any other agent's record clears on its
  stop even with background work left (ddon-data, 2026-10-17: a finished general-purpose
  researcher with one leftover background shell kept its record and blocked the next spawn).
- `check` (PreToolUse on `Agent`): refuses (exit 2, message on stderr) a spawn that is not a
  project role or not titled (below), then one made while a running record younger than 4 h exists,
  naming the agent, its type and its age. Records older than 4 h are stale: ignored and deleted.
  `SendMessage` (resuming an agent) is never refused.
  The spawn guard (ported from the reconstructor's guard_agent, 002 F6): `subagent_type` is a stem
  of `.claude/agents/*.md`, or `general-purpose` with a prompt starting "Your role is"
  (orchestration section 2); the description is `<role> · <spec> <package>: <what>`
  (`implementer · 002 P4: reconstructor-port wave 2`), its role the agent's own (an `-ida` variant
  may name its base role) or, for `general-purpose`, any project role. No committed-brief check:
  ddon-data commits records after landing. When `.claude/agents/` holds no role, the guard is off.

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
RECEIPT_ROLES = {"implementer"}
GENERAL = "general-purpose"
ROLE_PROMPT = "Your role is"
TITLE = re.compile(r"^(?P<role>[\w-]+) · (?P<spec>\d{3}) (?P<package>\S+?): \S")
TITLE_EXAMPLE = "implementer · 002 P4: reconstructor-port wave 2"
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
    agent = agent_of(data)
    if (count(data.get("background_tasks")) > 0 and not finished(data)
            and recorded_type(agent) in RECEIPT_ROLES):
        return 0
    if agent != "unknown":
        (running_dir() / f"{agent}.json").unlink(missing_ok=True)
    return 0


def recorded_type(agent):
    """The agent type its start record names, or None."""
    try:
        record = json.loads((running_dir() / f"{agent}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return record.get("agent_type") if isinstance(record, dict) else None


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


def roles():
    """The project's roles: the stems of `.claude/agents/*.md`, sorted."""
    directory = hooklib.REPO / ".claude" / "agents"
    try:
        return sorted(path.stem for path in directory.glob("*.md") if path.stem)
    except OSError:
        return []


def spawn_problems(inp, known):
    """What is wrong with a spawn's type and title; empty when it is a titled project role."""
    role = inp.get("subagent_type") if isinstance(inp.get("subagent_type"), str) else ""
    title = inp.get("description") if isinstance(inp.get("description"), str) else ""
    prompt = inp.get("prompt") if isinstance(inp.get("prompt"), str) else ""
    found = []
    general = role == GENERAL and prompt.lstrip().startswith(ROLE_PROMPT)
    if role not in known and not general:
        found.append(f"`subagent_type` is {role or 'missing'}: spawn one of the project's roles "
                     f"({', '.join(known)}), or `{GENERAL}` with a prompt starting \"{ROLE_PROMPT}\" "
                     f"(orchestration section 2); never another built-in type or a fork")
    match = TITLE.match(title)
    if match is None:
        found.append(f"the description {title!r} is not `<role> · <spec> <package>: <what>` (`{TITLE_EXAMPLE}`)")
    elif role in known and match["role"] != role and not (
            role.endswith("-ida") and match["role"] == role.removesuffix("-ida") and match["role"] in known):
        found.append(f"the description names the role {match['role']!r}, the agent is a {role!r}")
    elif general and match["role"] not in known:
        found.append(f"the description names {match['role']!r}, which is not a project role ({', '.join(known)})")
    return found


def check(data):
    if data.get("tool_name") == "SendMessage":
        return 0
    inp = data.get("tool_input")
    known = roles()
    if isinstance(inp, dict) and known:
        found = spawn_problems(inp, known)
        if found:
            reason = "Refused: " + "; ".join(found) + "."
            hooklib.record_refusal(data, "agent_cap", reason)
            print(reason, file=sys.stderr)
            return 2
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
