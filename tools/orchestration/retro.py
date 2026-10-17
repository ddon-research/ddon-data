"""Efficiency retrospective: one summary of a window's agent work, with no model turn.

  python -X utf8 -I tools/orchestration/retro.py --since 2026-10-17 --label "010 end" [--until ISO]
         [--append] [--out specs/<feature>/research/retro-<label>.md]

Reads two sources:
- the tool-call ledger `.agent-ledger/tool-calls.jsonl` (tools/hooks/log_tool.py and the guards):
  calls per tool, failures, refusals by guard, repeated commands, the slowest calls and the
  largest results (a result's characters / 4 approximates the tokens it adds to every later turn);
- Claude Code's transcripts for this project (`~/.claude/projects/<project>/`): per session and
  subagent, the turns, input/cache/output tokens, the peak context and the wall time.

Prints a Markdown report (or writes it to `--out`); `--append` adds one JSON row of the headline
metrics to `specs/efficiency-ledger.jsonl`, so each retrospective can be compared with the last.
"""

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEDGER = REPO / ".agent-ledger" / "tool-calls.jsonl"
HISTORY = REPO / "specs" / "efficiency-ledger.jsonl"


def project_dir(repo=REPO):
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(repo))
    return Path.home() / ".claude" / "projects" / slug


def moment(text):
    """An ISO date or time as an aware datetime (a bare date is local midnight)."""
    value = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    return value if value.tzinfo else value.astimezone()


def in_window(stamp, since, until):
    try:
        at = moment(stamp)
    except (TypeError, ValueError):
        return False
    return since <= at and (until is None or at <= until)


def ledger_rows(path, since, until):
    rows = []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if in_window(row.get("at"), since, until):
            rows.append(row)
    return rows


def transcript_usage(path, since, until):
    """Turns, token sums, the peak context and the first/last timestamps of one transcript."""
    seen, out = {}, {"turns": 0, "input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "peak": 0,
                        "first": None, "last": None, "model": None}
    try:
        handle = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return out
    # One response is logged as several lines (one per content block) with the same id; the
    # last line carries the final output count, so the last usage per id wins.
    with handle:
        for line in handle:
            if '"usage"' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            message = entry.get("message") or {}
            usage = message.get("usage")
            stamp = entry.get("timestamp")
            if usage and in_window(stamp, since, until):
                seen[message.get("id") or f"line{len(seen)}"] = (stamp, usage, message.get("model"))
    for stamp, usage, model in sorted(seen.values(), key=lambda item: moment(item[0])):
        out["turns"] += 1
        out["input"] += int(usage.get("input_tokens") or 0)
        out["cache_write"] += int(usage.get("cache_creation_input_tokens") or 0)
        out["cache_read"] += int(usage.get("cache_read_input_tokens") or 0)
        out["output"] += int(usage.get("output_tokens") or 0)
        context = sum(int(usage.get(k) or 0) for k in
                      ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        out["peak"] = max(out["peak"], context)
        out["first"] = out["first"] or stamp
        out["last"] = stamp
        out["model"] = model or out["model"]
    return out


def transcripts(directory, since, until):
    """One usage record per main session and subagent active in the window."""
    records = []
    directory = Path(directory)
    if not directory.is_dir():
        return records
    floor = since.timestamp()
    candidates = [(p, "main", p.stem) for p in directory.glob("*.jsonl")]
    candidates += [(p, "subagent", p.stem) for p in directory.glob("*/subagents/agent-*.jsonl")]
    for path, kind, name in candidates:
        if path.stat().st_mtime < floor:
            continue
        usage = transcript_usage(path, since, until)
        if not usage["turns"]:
            continue
        label = name
        meta = path.with_name(path.stem + ".meta.json")
        if meta.exists():
            try:
                info = json.loads(meta.read_text(encoding="utf-8"))
                label = f"{info.get('agentType')}: {info.get('description')}"
            except (OSError, ValueError):
                pass
        records.append({"kind": kind, "name": label, **usage})
    return records


def wall_hours(record):
    try:
        return (moment(record["last"]) - moment(record["first"])).total_seconds() / 3600
    except (TypeError, ValueError, KeyError):
        return 0.0


def metrics(rows, records):
    calls = [r for r in rows if r.get("event") in ("call", "failed")]
    refused = [r for r in rows if r.get("event") == "refused"]
    failed = [r for r in calls if r.get("event") == "failed"]
    total = len(calls) + len(refused)
    subagents = [r for r in records if r["kind"] == "subagent"]
    peaks = sorted(r["peak"] for r in subagents)
    return {
        "calls": len(calls),
        "failed_pct": round(100 * len(failed) / total, 2) if total else 0.0,
        "refused_pct": round(100 * len(refused) / total, 2) if total else 0.0,
        "result_tokens_est": sum(int(r.get("response_chars") or 0) for r in calls) // 4,
        "sessions": sum(r["kind"] == "main" for r in records),
        "subagents": len(subagents),
        "turns": sum(r["turns"] for r in records),
        "tokens_input": sum(r["input"] + r["cache_write"] + r["cache_read"] for r in records),
        "tokens_output": sum(r["output"] for r in records),
        "main_peak_context": max((r["peak"] for r in records if r["kind"] == "main"), default=0),
        "subagent_peak_median": peaks[len(peaks) // 2] if peaks else 0,
        "agent_hours": round(sum(wall_hours(r) for r in subagents), 2),
    }


def report(label, since, until, rows, records):
    m = metrics(rows, records)
    calls = [r for r in rows if r.get("event") in ("call", "failed")]
    out = [f"# Efficiency retrospective: {label}", "",
           f"Window: {since.isoformat(timespec='minutes')} to {until.isoformat(timespec='minutes') if until else 'now'}.",
           "", "## Headline", ""]
    out += [f"- {key}: {value:,}" if isinstance(value, int) else f"- {key}: {value}" for key, value in m.items()]
    by_tool = collections.Counter(r.get("tool") for r in calls)
    out += ["", "## Calls per tool", ""] + ([f"- {tool}: {n}" for tool, n in by_tool.most_common(12)] or ["- none"])
    refusals = collections.Counter((r.get("hook"), r.get("reason", "")[:90]) for r in rows if r.get("event") == "refused")
    out += ["", "## Refusals (guard: reason)", ""] + (
        [f"- {n} x {hook}: {reason}" for (hook, reason), n in refusals.most_common(10)] or ["- none"])
    failures = collections.Counter((r.get("tool"), (r.get("error") or "")[:90]) for r in calls if r.get("event") == "failed")
    out += ["", "## Failures (tool: error)", ""] + (
        [f"- {n} x {tool}: {error}" for (tool, error), n in failures.most_common(10)] or ["- none"])
    repeated = collections.Counter((r.get("agent") or "main", r.get("cmd")) for r in calls
                                   if r.get("tool") in ("Bash", "PowerShell") and r.get("cmd"))
    out += ["", "## Repeated commands (same agent, 3 or more)", ""] + (
        [f"- {n} x [{agent}] `{cmd[:120]}`" for (agent, cmd), n in repeated.most_common(10) if n >= 3] or ["- none"])
    slow = sorted((r for r in calls if r.get("duration_ms")), key=lambda r: -r["duration_ms"])[:8]
    out += ["", "## Slowest calls", ""] + (
        [f"- {r['duration_ms'] / 1000:.1f} s {r.get('tool')} `{(r.get('cmd') or '')[:120]}`" for r in slow] or ["- none"])
    large = sorted(calls, key=lambda r: -int(r.get("response_chars") or 0))[:8]
    out += ["", "## Largest results (each re-read on every later turn)", ""] + (
        [f"- ~{int(r.get('response_chars') or 0) // 4000}k tokens {r.get('tool')} `{(r.get('cmd') or '')[:120]}`"
         for r in large if r.get("response_chars")] or ["- none"])
    costly = sorted(records, key=lambda r: -(r["cache_read"] + r["cache_write"] + r["input"]))[:10]
    out += ["", "## Sessions and agents by input tokens", "",
            "| kind | name | turns | input+cache (k) | output (k) | peak (k) | wall (h) |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    out += [f"| {r['kind']} | {r['name'][:60]} | {r['turns']} | {(r['input'] + r['cache_write'] + r['cache_read']) // 1000:,} "
            f"| {r['output'] // 1000:,} | {r['peak'] // 1000:,} | {wall_hours(r):.2f} |" for r in costly]
    return "\n".join(out) + "\n", m


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--since", required=True)
    parser.add_argument("--until")
    parser.add_argument("--label", required=True)
    parser.add_argument("--ledger", default=str(LEDGER))
    parser.add_argument("--transcripts", default=str(project_dir()))
    parser.add_argument("--history", default=str(HISTORY))
    parser.add_argument("--out")
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args(argv)
    since = moment(args.since)
    until = moment(args.until) if args.until else None
    rows = ledger_rows(args.ledger, since, until)
    records = transcripts(args.transcripts, since, until)
    text, m = report(args.label, since, until, rows, records)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text)
    if args.append:
        row = {"label": args.label, "since": since.isoformat(), "until": until.isoformat() if until else None,
               "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "metrics": m}
        with open(args.history, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row) + "\n")
        print(f"appended a row to {args.history}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
