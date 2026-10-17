"""PreToolUse guard for the Read tool: the first whole read of a large text file is refused once,
with the way to read part of it; asking again reads the whole file.

Why: a tool result stays in the context for every later turn, so a 200 KB log or IDA export read
whole is paid for again on each turn (the reference project measured file reads at 39% of what
subagents re-read). It is a nudge, not a wall: the second whole read of the same file by the same
agent runs. A read with `offset` or `limit`, a file under the threshold, and images/PDFs pass.
"""

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

SIZE = 100_000
MARKDOWN_SIZE = 40_000
BINARY_VIEWS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".pdf", ".ipynb"}


def verdict(data):
    """The refusal text, or None. A refusal is recorded so the agent's next whole read runs."""
    inp = data.get("tool_input") or {}
    path = inp.get("file_path") or ""
    if not path or inp.get("offset") or inp.get("limit") or inp.get("pages"):
        return None
    suffix = Path(path).suffix.lower()
    if suffix in BINARY_VIEWS:
        return None
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    if size < (MARKDOWN_SIZE if suffix in (".md", ".adoc") else SIZE):
        return None
    key = f"{hooklib.caller_key(data)}|{os.path.normcase(os.path.abspath(path))}"
    directory = Path(os.environ.get("DDON_HOOK_READ_DIR") or hooklib.ledger_dir() / "reads")
    stamp = directory / hashlib.sha1(key.encode()).hexdigest()
    if stamp.exists():
        return None
    try:
        directory.mkdir(parents=True, exist_ok=True)
        stamp.write_text(path, encoding="utf-8")
    except OSError:
        return None
    return (f"{path} is {size // 1000} KB; a whole read stays in your context for every later turn "
            f"(about {size // 4000}k tokens). Read the part you need with offset/limit, or locate it first with "
            f"`rg -n -m 20 PATTERN FILE`. If you really need all of it, Read it again: the next whole read runs.")


def main():
    data = hooklib.read_input()
    if not data or data.get("tool_name") != "Read":
        return 0
    reason = verdict(data)
    if reason:
        hooklib.record_refusal(data, "guard_read", reason)
        print(f"Refused once: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    hooklib.fail_open(main)
