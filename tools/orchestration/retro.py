"""Efficiency retrospective: one summary of a window's agent work, with no model turn.

  python -X utf8 -I tools/orchestration/retro.py --since 2026-10-17 --label "010 end" [--until ISO]
         [--append] [--out specs/<feature>/research/retro-<label>.md]

Reads two sources:
- the tool-call ledger `.agent-ledger/tool-calls.jsonl` (tools/hooks/log_tool.py and the guards):
  calls per tool, failures, refusals by guard, repeated commands, the slowest calls and the
  largest results (a result's characters / 4 approximates the tokens it adds to every later turn);
- Claude Code's transcripts for this project (`~/.claude/projects/<project>/`): per session and
  subagent, the turns, input/cache/output tokens, the peak context, the wall time and list $.

Prints a Markdown report (or writes it to `--out`); `--append` adds one JSON row of the headline
metrics to `specs/efficiency-ledger.jsonl`, so each retrospective can be compared with the last.
Each row carries `head` (the git sha) and `unavailable` {metric: reason}.

Dollars are list prices (`PRICES`, `cost()`, ported from the reconstructor's
`tools/orchestration/orch/transcripts.py`). A model missing from `PRICES` is never guessed: its
responses are left out of `cost.*` and named under `unavailable`. Budget overruns come from the
`Budget: N min|h` or `budget N min` line of the brief named in the agent's spawn prompt (else the
prompt itself); an agent with neither is named under `unavailable`.
"""

import argparse
import collections
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEDGER = REPO / ".agent-ledger" / "tool-calls.jsonl"
HISTORY = REPO / "specs" / "efficiency-ledger.jsonl"

# List prices per million tokens, Anthropic first-party API (the reconstructor's
# orch/transcripts.py: the bundled claude-api skill's model table, cached 2026-10-06). Cache writes
# cost 1.25x input for 5 minutes and 2x for 1 hour; fast mode doubles input and output.
PRICES = {
    "claude-opus-5-5": {"in": 4.00, "out": 20.00, "read": 0.20},
    "claude-opus-5": {"in": 5.00, "out": 25.00, "read": 0.50},
    "claude-fable-5-1": {"in": 10.00, "out": 50.00, "read": 0.25},
    "claude-fable-5": {"in": 10.00, "out": 50.00, "read": 1.00},
    "claude-sonnet-5-5": {"in": 2.00, "out": 10.00, "read": 0.20},
    "claude-sonnet-5": {"in": 2.00, "out": 10.00, "read": 0.20},
    "claude-haiku-5-5": {"in": 0.10, "out": 0.50, "read": 0.01},
    "claude-opus-4-8": {"in": 5.00, "out": 25.00, "read": 0.50},
    "claude-opus-4-7": {"in": 5.00, "out": 25.00, "read": 0.50},
    "claude-opus-4-6": {"in": 5.00, "out": 25.00, "read": 0.50},
    "claude-sonnet-4-6": {"in": 3.00, "out": 15.00, "read": 0.30},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00, "read": 0.10},
}
BUDGET = re.compile(r"\bbudget:?\s+(\d+(?:\.\d+)?)\s*(min|minutes?|h|hours?)\b", re.I)
BRIEF = re.compile(r"(?:[A-Za-z]:)?[\w./\\-]*briefs[\\/][\w.-]+\.md")
INSTRUCTIONS = {  # metric: files relative to the repo (globs allowed)
    "instructions.agents_md_tokens": ["AGENTS.md"],
    "instructions.claude_md_tokens": ["CLAUDE.md"],
    "instructions.roles_tokens": [".claude/agents/*.md"],
    "instructions.skill_tokens": [".claude/skills/coordinate/*.md"],
}


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
    except (TypeError, ValueError, AttributeError):
        return False
    return since <= at and (until is None or at <= until)


def model_key(model):
    """A transcript's model name as a `PRICES` key: `[1m]` and a `-YYYYMMDD` suffix dropped."""
    return re.sub(r"-\d{8}$", "", re.sub(r"\[.*?\]$", "", str(model or "")))


def token_classes(usage):
    """(input, output, 5-minute writes, 1-hour writes, cache reads) of one response's usage."""
    usage = usage or {}
    creation = usage.get("cache_creation") or {}
    w1h = int(creation.get("ephemeral_1h_input_tokens") or 0)
    w5 = creation.get("ephemeral_5m_input_tokens")
    w5 = int(usage.get("cache_creation_input_tokens") or 0) - w1h if w5 is None else int(w5)
    return (int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0), w5, w1h,
            int(usage.get("cache_read_input_tokens") or 0))


def cost(model, usage):
    """List dollars of one response, or None for a model without a price (never guessed)."""
    price = PRICES.get(model_key(model))
    if price is None:
        return None
    tin, tout, w5, w1h, read = token_classes(usage)
    fast = 2.0 if (usage or {}).get("speed") == "fast" else 1.0
    return (tin * price["in"] * fast + tout * price["out"] * fast
            + w5 * price["in"] * 1.25 + w1h * price["in"] * 2.0 + read * price["read"]) / 1e6


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


def first_prompt(line):
    """The text of a user record (the spawn prompt when it is the first), else None."""
    try:
        entry = json.loads(line)
    except ValueError:
        return None
    if entry.get("type") != "user":
        return None
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        content = " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return content if isinstance(content, str) and content else None


def transcript_usage(path, since, until):
    """Turns, token sums, list $, the peak context and the first/last timestamps of one transcript."""
    seen, out = {}, {"turns": 0, "input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "peak": 0,
                     "first": None, "last": None, "model": None, "usd": 0.0, "unpriced": {}, "prompt": None}
    try:
        handle = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return out
    # One response is logged as several lines (one per content block) with the same id; the
    # last line carries the final output count, so the last usage per id wins.
    with handle:
        for line in handle:
            if out["prompt"] is None and '"user"' in line:
                out["prompt"] = first_prompt(line)
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
        usd = cost(model, usage)
        if usd is not None:
            out["usd"] += usd
        elif any(token_classes(usage)):  # a zero-token record (`<synthetic>`) costs nothing
            key = model_key(model) or "(no model)"
            out["unpriced"][key] = out["unpriced"].get(key, 0) + 1
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
        records.append({"kind": kind, "name": label, "id": name, **usage})
    return records


def wall_hours(record):
    try:
        return (moment(record["last"]) - moment(record["first"])).total_seconds() / 3600
    except (TypeError, ValueError, KeyError, AttributeError):
        return 0.0


def budget_minutes(record, repo=REPO):
    """The budget in minutes from the brief named in the spawn prompt (else the prompt), or None."""
    prompt = record.get("prompt") or ""
    texts = []
    for found in BRIEF.findall(prompt):
        path = Path(found.replace("\\", "/"))
        for candidate in (path, Path(repo) / path):
            if candidate.is_file():
                try:
                    texts.append(candidate.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    pass
                break
    for text in texts + [prompt]:
        match = BUDGET.search(text)
        if match:
            value = float(match.group(1))
            return value if match.group(2).lower().startswith("m") else value * 60
    return None


def git_head(repo=REPO):
    try:
        done = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=False, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() or None


def chars_tokens(paths):
    return sum(len(p.read_text(encoding="utf-8", errors="replace")) for p in paths) // 4


def spend(records):
    """(total $, coordinator $) of a window's records."""
    return sum(r["usd"] for r in records), sum(r["usd"] for r in records if r["kind"] == "main")


def extended(records, repo=REPO):
    """The cost, instruction and budget metrics, and {metric: reason} for those unavailable."""
    repo = Path(repo)
    m, unavailable = {}, {}
    subagents = [r for r in records if r["kind"] == "subagent"]
    total, coordinator = spend(records)
    m["cost.total_usd"] = round(total, 2)
    m["cost.coordinator_usd"] = round(coordinator, 2)
    if total:
        m["cost.coordinator_share_pct"] = round(100 * coordinator / total, 1)
    else:
        unavailable["cost.coordinator_share_pct"] = "no priced spend in the window"
    per_agent = {}
    for r in sorted(subagents, key=lambda r: -r["usd"]):
        key = r["name"] if r["name"] not in per_agent else f"{r['name']} ({r['id']})"
        per_agent[key] = round(r["usd"], 2)
    m["cost.per_agent_usd"] = per_agent
    unpriced = collections.Counter()
    for r in records:
        unpriced.update(r.get("unpriced") or {})
    if unpriced:
        unavailable["cost.unpriced_models"] = "no list price, left out of cost.*: " + ", ".join(
            f"{model} ({n} responses)" for model, n in unpriced.most_common())
    for key, patterns in INSTRUCTIONS.items():
        files = sorted({p for pattern in patterns for p in repo.glob(pattern) if p.is_file()})
        if files:
            m[key] = chars_tokens(files)
        else:
            unavailable[key] = f"no {' or '.join(patterns)} in {repo}"
    budgeted, unknown, over, over2 = 0, [], 0, 0
    for r in subagents:
        budget = budget_minutes(r, repo)
        if budget is None:
            unknown.append(r["name"])
            continue
        budgeted += 1
        minutes = wall_hours(r) * 60
        over += minutes > budget
        over2 += minutes > 2 * budget
    if budgeted:
        m["waste.budget_overruns_1x"] = over
        m["waste.budget_overruns_2x"] = over2
        if unknown:
            unavailable["waste.budget_unknown"] = (f"{len(unknown)} agents without a budget in their brief or prompt: "
                                                   + "; ".join(unknown[:10]))
    else:
        reason = "no agent's brief or prompt names a budget" if subagents else "no subagent in the window"
        unavailable["waste.budget_overruns_1x"] = unavailable["waste.budget_overruns_2x"] = reason
    return m, unavailable


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


def report(label, since, until, rows, records, repo=REPO):
    m = metrics(rows, records)
    more, unavailable = extended(records, repo)
    m.update(more)
    calls = [r for r in rows if r.get("event") in ("call", "failed")]
    out = [f"# Efficiency retrospective: {label}", "",
           f"Window: {since.isoformat(timespec='minutes')} to {until.isoformat(timespec='minutes') if until else 'now'}.",
           "", "## Headline", ""]
    out += [f"- {key}: {value:,}" if isinstance(value, int) else f"- {key}: {value}" for key, value in m.items()
            if not isinstance(value, dict)]
    out += ["", "## Cost per agent (list $)", ""] + (
        [f"- ${usd:,.2f} {name[:80]}" for name, usd in m["cost.per_agent_usd"].items()] or ["- none"])
    out += ["", "## Unavailable", ""] + ([f"- {key}: {why}" for key, why in unavailable.items()] or ["- none"])
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
            "| kind | name | turns | input+cache (k) | output (k) | peak (k) | wall (h) | $ |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    out += [f"| {r['kind']} | {r['name'][:60]} | {r['turns']} | {(r['input'] + r['cache_write'] + r['cache_read']) // 1000:,} "
            f"| {r['output'] // 1000:,} | {r['peak'] // 1000:,} | {wall_hours(r):.2f} | {r['usd']:,.2f} |" for r in costly]
    return "\n".join(out) + "\n", m, unavailable


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--since", required=True)
    parser.add_argument("--until")
    parser.add_argument("--label", required=True)
    parser.add_argument("--ledger", default=str(LEDGER))
    parser.add_argument("--transcripts", default=str(project_dir()))
    parser.add_argument("--history", default=str(HISTORY))
    parser.add_argument("--repo", default=str(REPO), help=argparse.SUPPRESS)
    parser.add_argument("--out")
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args(argv)
    since = moment(args.since)
    until = moment(args.until) if args.until else None
    rows = ledger_rows(args.ledger, since, until)
    records = transcripts(args.transcripts, since, until)
    text, m, unavailable = report(args.label, since, until, rows, records, Path(args.repo))
    head = git_head(args.repo)
    if head is None:
        unavailable["head"] = "git rev-parse HEAD failed"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text)
    if args.append:
        row = {"label": args.label, "since": since.isoformat(), "until": until.isoformat() if until else None,
               "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "head": head,
               "metrics": m, "unavailable": unavailable}
        with open(args.history, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row) + "\n")
        print(f"appended a row to {args.history}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
