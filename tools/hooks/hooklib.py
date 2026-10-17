"""Shared helpers for the Claude Code hooks in this folder.

Every hook reads one JSON object on stdin (the hook input), decides, and exits:
0 lets the call run, 2 refuses it and shows stderr to the model. A hook never refuses on its own
failure: every entry point wraps its work in `fail_open`, so an internal error exits 0.

The ledger lives in the main checkout's `.agent-ledger/` (gitignored), because settings.json calls
these scripts by their absolute main-checkout path, also from a worktree agent. Tests point it
elsewhere with `DDON_HOOK_LEDGER_DIR`.
"""

import datetime as dt
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def ledger_dir():
    return Path(os.environ.get("DDON_HOOK_LEDGER_DIR") or REPO / ".agent-ledger")


def read_input(stream=None):
    """The hook input as a dict, or None when stdin is not a JSON object."""
    try:
        data = json.load(stream or sys.stdin)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def now_iso():
    return dt.datetime.now().astimezone().isoformat(timespec="milliseconds")


def caller_key(data):
    """One key per session and agent: the main session and each subagent get their own state."""
    return "|".join(str(data.get(k) or "") for k in ("session_id", "agent_id", "transcript_path"))


def append(name, row):
    """Append one JSON line to `<ledger>/<name>`; silently does nothing on failure."""
    try:
        directory = ledger_dir()
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / name, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    except OSError:
        pass


def record_refusal(data, hook, reason):
    """Log a refusal, so the retrospective counts refused calls by class."""
    inp = data.get("tool_input") or {}
    append("tool-calls.jsonl", {
        "at": now_iso(),
        "event": "refused",
        "hook": hook,
        "tool": data.get("tool_name"),
        "session": data.get("session_id"),
        "agent": data.get("agent_id"),
        "agent_type": data.get("agent_type"),
        "cmd": str(inp.get("command") or inp.get("file_path") or "")[:200],
        "reason": reason.split("\n", 1)[0][:200],
    })


def fail_open(main):
    """Run `main()`; any exception exits 0 so a broken hook never blocks work."""
    try:
        code = main()
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else 0
    except Exception:  # noqa: BLE001 - a hook must never fail the call it watches
        code = 0
    sys.exit(code or 0)
