# R1 findings: the reconstructor's agentic setup and ddon-data's gaps

Source: a `repository-researcher` that read `C:\ddon-dwarf-reconstructor-rust` (working tree as of
2026-10-17) and ddon-data at 65c778c. It read files only and ran nothing.

## Mechanisms we lack or have only partly (reconstructor paths)

- **Usage readings:** `tools/hooks/log_usage.py` is a PostToolUse hook on `get_usage`. It appends
  `{at, weekly, weekly_resets_at, five_hour}` to a JSONL. We have the rule as text only.
- **$ and spend:** `tools/orchestration/orch/transcripts.py:31-38` has a price table and computes the
  cost of each response. `usage_report.py` writes `specs/<spec>/usage.md`, with turns, tool uses,
  tokens by class (in, out, w5m, w1h, read), wall time, $ and models. We have none of this.
- **Progress block:** `progress.py` prints one bar per spec from `tasks.md`, then spend, an efficiency
  line and a context line. It starts every report to the user. We have none.
- **Context line:** `context_size.py` gives tokens and $/turn, with compact advice at 700k and 850k.
  We have thresholds only.
- **Subagent stop record:** `subagent_stop.py` writes `stops.jsonl` and saves each report to a file.
  It records report size and `waiting:`/`blocked:` prefixes. Reports took 1.10M characters of the
  coordinator's context there. We have none.
- **Session state:** `session_state.py` covers start, compact, resume and subagent start. It injects
  progress and "resume here", and a diff of instruction files changed since load. We have none.
- **Section reader:** `section.py` lets briefs cite a heading instead of a file. We have none.
- **retro.py:** about 70 metrics: cost (including the coordinator's share), context and re-reads,
  cache TTL, waste, budget overruns, instruction tokens, `head`, `unavailable`. Ours has 13 and no $.
- **Ledger:** there it is `specs/efficiency-ledger.jsonl`. Ours does not exist yet.
- **Learnings:** `specs/*-learnings/` (brief, learnings, review, applied), plus `.claude/rules/*.md`
  scoped with `paths:`. We have the 15-entry `CLAUDE.md` list.
- **Spec end (C1):** docs check, a 45-minute whole-spec review, a docs audit, the full retro (a
  researcher on the outliers, 60 min), learnings, status done, then `main` and push. We had none;
  now `specs/orchestration.md` section 10.
- **Subagent compaction:** `autoCompactWindow: 400000` on the roles. Their p90 peak was 630k. Added
  here (T003).

## Ranked ports (benefit per cost)

1. $ in `retro.py` and the ledger (about 1 h). The coordinator was 17% of spend there; implementer
   cost fell from $17 to $10 once it was measured.
2. `log_usage.py` (15 min).
3. `progress.py` for ddon-data's task conventions (about 1 h).
4. The spec-end checklist (text; done as orchestration section 10).
5. `subagent_stop.py` (20 min).
6. `autoCompactWindow` (done).
7. `session_state.py` without worktrees (1.5 h).
8. `section.py` (5 min).
9. `.claude/rules/` scoped learnings (1 h).
10. The Claude Code guidance digest, at full retros only.

## Not ported

- The worktree, train, golden and corpus tools.
- `receipt.py --verify` (built on cargo xtask).
- The pipeline metrics.
- The structure tools.
- `effort`.
- `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`.
- efficiency.py, context_report.py and context_growth.py as separate scripts: their metrics go into
  `retro.py`.

## Not verified

The researcher read `context_watch.py`, `usage_report.py` and `progress.py` only up to their
docstrings. The actual retros live in `specs/029-performance-tuning/research/retro-*.md`, not in
`specs/efficiency-retrospectives/`.
