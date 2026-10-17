"""Tool-call ledger: one JSON line per tool call in `.agent-ledger/tool-calls.jsonl` (gitignored).

Wired in `.claude/settings.json` on three events:
- PreToolUse (slow tools only): stamps the call's start under `.agent-ledger/inflight/`;
- PostToolUse and PostToolUseFailure: append the row and drop the stamp.

A row: `at`, `event` (`call` or `failed`), `tool`, `session`, `agent`, `agent_type`, `ok`,
`duration_ms` (from the hook input when Claude Code supplies it, else from the stamp, else absent),
`input_chars`, `response_chars` (a proxy for the context the result costs: about 4 chars a token),
`cmd` (a Bash/PowerShell command, a file path or a subagent type, cut to 200 chars) and `error`.
The guards append `refused` rows to the same file. `tools/orchestration/retro.py` summarizes it.
The hook never blocks: every failure exits 0.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402


def stamp_path(data):
    call = "".join(c for c in str(data.get("tool_use_id") or "") if c.isalnum() or c in "-_")
    return hooklib.ledger_dir() / "inflight" / call if call else None


def summary(inp, tool):
    if not isinstance(inp, dict):
        return ""
    for key in ("command", "file_path", "notebook_path", "pattern", "url", "subagent_type", "query"):
        if inp.get(key):
            value = str(inp[key])
            if key == "subagent_type":
                value = f"{value}: {inp.get('description') or ''}"
            return value.replace("\n", " ")[:200]
    return tool if tool.startswith("mcp__") else ""


def failure(data):
    """The error text when the call failed, else None."""
    if data.get("hook_event_name") == "PostToolUseFailure":
        return str(data.get("error") or data.get("tool_response") or "failed")[:300]
    response = data.get("tool_response")
    if isinstance(response, dict):
        if response.get("is_error") or response.get("isError"):
            return json.dumps(response)[:300]
        if response.get("interrupted"):
            return "interrupted"
    return None


def row(data, now):
    tool = str(data.get("tool_name") or "")
    error = failure(data)
    out = {
        "at": hooklib.now_iso(),
        "event": "failed" if error else "call",
        "tool": tool,
        "session": data.get("session_id"),
        "agent": data.get("agent_id"),
        "agent_type": data.get("agent_type"),
        "ok": error is None,
        "input_chars": len(json.dumps(data.get("tool_input") or {}, ensure_ascii=False)),
        "response_chars": len(json.dumps(data.get("tool_response") or data.get("error") or "", ensure_ascii=False)),
        "cmd": summary(data.get("tool_input"), tool),
    }
    duration = data.get("duration_ms")
    stamp = stamp_path(data)
    if duration is None and stamp is not None:
        try:
            duration = round((now - float(stamp.read_text(encoding="utf-8"))) * 1000)
        except (OSError, ValueError):
            duration = None
    if duration is not None:
        out["duration_ms"] = duration
    if error:
        out["error"] = error
    if stamp is not None:
        try:
            stamp.unlink()
        except OSError:
            pass
    return out


def main():
    data = hooklib.read_input()
    if not data:
        return 0
    now = time.time()
    if data.get("hook_event_name") == "PreToolUse":
        stamp = stamp_path(data)
        if stamp is not None:
            stamp.parent.mkdir(parents=True, exist_ok=True)
            stamp.write_text(repr(now), encoding="utf-8")
        return 0
    hooklib.append("tool-calls.jsonl", row(data, now))
    return 0


if __name__ == "__main__":
    hooklib.fail_open(main)
