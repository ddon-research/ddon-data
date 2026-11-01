"""PreToolUse guard for ida-mcp's open_database: only a private copy made by
research/ida/private-copy.sh may be opened.

Why: the ida-mcp worker saves what it opens (on close, on shutdown, after execute_python), and the
user's IDA 9.5 databases may be open in the GUI at the same time. A copy lives at
D:/research/DDON-binaries/IDA9.5/<database folder>/ddon-data-<name>/<file>.i64; any other path,
or a call with no path, is refused with the command that makes a copy.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

COPY = re.compile(
    r"d:/research/ddon-binaries/ida9\.5/(pc_ddon_03040008|ps4_ddon_02020005_2016_12_21)"
    r"/ddon-data-[a-z0-9][a-z0-9_-]{0,63}/[^/]+\.i64")
ADVICE = ("open only a private copy: `bash research/ida/private-copy.sh <pc|ps4> <name>` prints its "
          "path; the user's .i64 may be open in the IDA GUI and the ida-mcp worker saves what it opens.")


def normalize(path):
    """`path` lower-cased with forward slashes, a Git Bash `/d/` prefix as `d:/`, `..` refused."""
    text = path.strip().replace("\\", "/").lower()
    if text.startswith("/d/"):
        text = "d:/" + text[3:]
    return None if "/../" in text or text.endswith("/..") else text


def verdict(data):
    """The refusal text, or None."""
    inp = data.get("tool_input") or {}
    path = inp.get("path") or inp.get("file_path") or inp.get("database") or ""
    if not path:
        return "open_database without a path: " + ADVICE
    text = normalize(path)
    if text and COPY.fullmatch(text):
        return None
    return f"{path} is not a private copy: " + ADVICE


def main():
    data = hooklib.read_input()
    if not data or not str(data.get("tool_name", "")).endswith("__open_database"):
        return 0
    reason = verdict(data)
    if reason:
        hooklib.record_refusal(data, "guard_ida", reason)
        print(f"Refused: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    hooklib.fail_open(main)
