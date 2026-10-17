"""The progress block that starts the coordinator's reports to Sam (about ten lines, no model turn).

  python -X utf8 -I tools/orchestration/progress.py [--since ISO] [--transcripts DIR] [--ledger-dir DIR]

- One line per open feature: every `specs/*/tasks.md` and `research/knowledge-graph/specs/*/tasks.md`
  without `**Status: done**` (also accepted: `**Status**: done` and `closed`, the spelling of
  `specs/001-ps4-static-dumps`). It shows the done `- [x]` and open `- [ ]` counts and the list $
  of the feature's window (retro.py's functions): from the first commit that touches the folder,
  or from `--since`. A folder no commit touches has no window and says so.
- The newest plan usage reading (`.agent-ledger/usage-readings.jsonl`, tools/hooks/log_usage.py).
- The coordinator's context: the last main-session response's tokens and $ a turn in cache reads,
  as in the reconstructor's `context_size.py` (a compaction after the last response makes it
  unavailable).
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import retro  # noqa: E402

FEATURES = ("specs/*/tasks.md", "research/knowledge-graph/specs/*/tasks.md")
DONE = re.compile(r"^\*\*Status(?:\*\*)?:\s*(?:done|closed)\b", re.I | re.M)  # a status line, not a quote of one
TICKED = re.compile(r"^\s*- \[[xX]\]", re.M)
OPEN = re.compile(r"^\s*- \[ \]", re.M)
WINDOW = 1_000_000
TAIL = 4_000_000  # bytes read from a transcript's end: enough for the last responses


def features(repo):
    """[(folder relative to the repo, done count, open count)] of the features not done."""
    found = []
    for pattern in FEATURES:
        for path in sorted(Path(repo).glob(pattern)):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if DONE.search(text):
                continue
            found.append((path.parent.relative_to(repo).as_posix(), len(TICKED.findall(text)), len(OPEN.findall(text))))
    return found


def first_commit(repo, folder):
    """The author time of the first commit touching the folder, or None."""
    try:
        done = subprocess.run(["git", "-C", str(repo), "log", "--reverse", "--format=%aI", "--", folder],
                              capture_output=True, text=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = done.stdout.split()
    return retro.moment(lines[0]) if lines else None


def bar(done, total, width=10):
    filled = round(width * done / total) if total else 0
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def spend_text(records):
    total, coordinator = retro.spend(records)
    agents = sum(r["kind"] == "subagent" for r in records)
    share = f", coordinator {100 * coordinator / total:.0f}%" if total else ""
    unpriced = sum(sum((r.get("unpriced") or {}).values()) for r in records)
    note = f" (+{unpriced} unpriced responses)" if unpriced else ""
    return f"${total:,.2f}{share}, {agents} agents{note}"


def newest_reading(ledger_dir):
    try:
        lines = (Path(ledger_dir) / "usage-readings.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and "weekly" in row:
            return row
    return None


def last_response(path):
    """(context tokens, model) of the last response in a transcript's tail, or None when there is
    none or a compaction came after it (the last response then shows the old context)."""
    with open(path, "rb") as handle:
        handle.seek(0, 2)
        handle.seek(max(0, handle.tell() - TAIL))
        tail = handle.read().decode("utf-8", errors="replace")
    for line in reversed(tail.splitlines()):
        if '"compact_boundary"' in line or ('"usage"' in line and '"assistant"' in line):
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
                return None
            message = entry.get("message") or {}
            tin, _, w5, w1h, read = retro.token_classes(message.get("usage"))
            if tin + w5 + w1h + read:
                return tin + w5 + w1h + read, message.get("model")
    return None


def context_text(directory):
    sessions = sorted(Path(directory).glob("*.jsonl"), key=lambda p: p.stat().st_mtime) if Path(directory).is_dir() else []
    found = last_response(sessions[-1]) if sessions else None
    if found is None:
        return "context: unavailable (no main-session transcript or no response since its last compaction)"
    tokens, model = found
    price = retro.PRICES.get(retro.model_key(model))
    turn = f"${tokens * price['read'] / 1e6:.2f} a turn in cache reads" if price else f"$ unavailable (no price for {model})"
    return f"context: {tokens // 1000:,}k of {WINDOW // 1000:,}k ({100 * tokens // WINDOW}%) · {turn}"


def block(repo, directory, ledger_dir, since=None):
    lines = [f"progress at {(retro.git_head(repo) or 'unknown')[:10]}, "
             f"{dt.datetime.now().astimezone().isoformat(sep=' ', timespec='minutes')}"]
    cache = {}
    for folder, done, todo in features(repo) or []:
        start = since or first_commit(repo, folder)
        if start is None:
            money = "spend unavailable (no commit touches the folder; pass --since)"
        else:
            if start not in cache:
                cache[start] = retro.transcripts(directory, start, None)
            money = f"since {start.date().isoformat()}: {spend_text(cache[start])}"
        lines.append(f"- {folder}: {bar(done, done + todo)} {done} done, {todo} open · {money}")
    if len(lines) == 1:
        lines.append("- no open feature (every tasks.md says done)")
    reading = newest_reading(ledger_dir)
    if reading:
        lines.append(f"usage: weekly {reading.get('weekly')}% (resets {reading.get('weekly_resets_at')}), "
                     f"5-hour {reading.get('five_hour')}%, read {reading.get('at')}")
    else:
        lines.append(f"usage: unavailable (no reading in {Path(ledger_dir) / 'usage-readings.jsonl'})")
    lines.append(context_text(directory))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--since", help="window start for every feature (default: its first commit)")
    parser.add_argument("--transcripts", default=str(retro.project_dir()))
    parser.add_argument("--ledger-dir", default=str(retro.REPO / ".agent-ledger"))
    parser.add_argument("--repo", default=str(retro.REPO), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    since = retro.moment(args.since) if args.since else None
    print(block(Path(args.repo), args.transcripts, args.ledger_dir, since))
    return 0


if __name__ == "__main__":
    sys.exit(main())
