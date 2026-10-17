"""PostToolUse hook on the usage tool: append the plan's readings to a local log.

Ported from the reconstructor's `tools/hooks/log_usage.py`. Each call of
`mcp__ccd_session_mgmt__get_usage` (the coordinator's usage gate) appends one line to
`.agent-ledger/usage-readings.jsonl` (gitignored; `DDON_HOOK_LEDGER_DIR` moves it for the tests):
{"at": <now, ISO>, "weekly": <percent>, "weekly_resets_at": <ISO>, "five_hour": <percent>}.
`tools/orchestration/progress.py` prints the newest line. The hook never blocks the call: every
failure, bad input included, exits 0 silently.
"""

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

NAME = "usage-readings.jsonl"


def payload(response):
    """The usage object, from a dict, a JSON string or MCP text blocks."""
    if isinstance(response, dict) and "plan" in response:
        return response
    if isinstance(response, str):
        return json.loads(response)
    blocks = response.get("content") if isinstance(response, dict) else response
    for block in blocks or []:
        if isinstance(block, dict) and block.get("type") == "text":
            return json.loads(block["text"])
    return None


def reading(usage):
    windows = {w.get("label"): w for w in (usage.get("plan") or {}).get("windows") or [] if isinstance(w, dict)}
    weekly = windows.get("Weekly · all models") or {}
    five = windows.get("5-hour limit") or {}
    if "percentUsed" not in weekly:
        return None
    return {
        "at": hooklib.now_iso(),
        "weekly": weekly["percentUsed"],
        "weekly_resets_at": weekly.get("resetsAt"),
        "five_hour": five.get("percentUsed"),
    }


def main():
    try:
        event = json.load(sys.stdin)
        usage = payload(event.get("tool_response"))
        row = reading(usage) if isinstance(usage, dict) else None
        if row:
            hooklib.append(NAME, row)
    except Exception:  # noqa: BLE001 - a hook must never fail the call it watches
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
