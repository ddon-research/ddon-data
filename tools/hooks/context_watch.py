"""PostToolUse and UserPromptSubmit hook for the main session: one reminder each time the
coordinator's context crosses a threshold, so it asks the user to `/compact` at a natural break
instead of drifting into the automatic compaction mid-step.

The context is the last response's input + cache-creation + cache-read tokens, read from the
transcript's tail. Subagents are skipped (their input carries `agent_id`). The state (the highest
threshold already reminded, per transcript) lives under `.agent-ledger/context-watch/` and resets
when the context falls below the first threshold (after a compaction). Never blocks; exits 0.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

THRESHOLDS = (300_000, 500_000, 700_000, 850_000, 930_000)
COMPACT_NOW = 700_000
TAIL = 1_000_000


def last_context(path):
    """The last response's context in tokens, or None."""
    with open(path, "rb") as handle:
        handle.seek(0, 2)
        handle.seek(max(0, handle.tell() - TAIL))
        tail = handle.read().decode("utf-8", errors="replace")
    for line in reversed(tail.splitlines()):
        if '"usage"' not in line or '"assistant"' not in line:
            continue
        try:
            usage = (json.loads(line).get("message") or {}).get("usage") or {}
        except ValueError:
            continue
        tokens = sum(int(usage.get(k) or 0) for k in
                     ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        if tokens:
            return tokens
    return None


def reminder(data):
    """The additionalContext text to add, or None."""
    if data.get("agent_id") or not data.get("transcript_path"):
        return None
    path = Path(data["transcript_path"])
    tokens = last_context(path)
    if not tokens:
        return None
    directory = Path(os.environ.get("DDON_HOOK_CONTEXT_DIR") or hooklib.ledger_dir() / "context-watch")
    stamp = directory / hashlib.sha1(str(path).encode()).hexdigest()
    try:
        reminded = int(stamp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        reminded = 0
    if tokens < THRESHOLDS[0]:
        if reminded:
            stamp.unlink(missing_ok=True)
        return None
    crossed = max(t for t in THRESHOLDS if t <= tokens)
    if crossed <= reminded:
        return None
    directory.mkdir(parents=True, exist_ok=True)
    stamp.write_text(str(crossed), encoding="utf-8")
    head = f"Context check: this session's context is {tokens // 1000}k tokens (over {crossed // 1000}k). "
    if tokens < COMPACT_NOW:
        todo = ("Finish the step in hand; at the next natural break, record state in the feature's tasks.md and "
                "ask the user to run /compact.")
    else:
        todo = ("Compact at this break: commit the records (tasks.md, receipts, running agent ids), then ask the "
                "user to run /compact. Spawn fresh agents with briefs instead of resuming large ones.")
    return head + todo


def main():
    data = hooklib.read_input()
    if not data:
        return 0
    text = reminder(data)
    if text:
        event = data.get("hook_event_name") or "PostToolUse"
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    hooklib.fail_open(main)
