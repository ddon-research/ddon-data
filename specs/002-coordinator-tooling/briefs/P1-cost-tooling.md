002 P1: cost, usage, progress and stop-record tooling

Objective: give the coordinator measured spend, plan usage and spec progress for its reports to
Sam, and record subagent reports in files. Port from the reconstructor
(R = C:\ddon-dwarf-reconstructor-rust, read-only) and adapt it to ddon-data, which has one checkout
and no worktrees. Background: `specs/002-coordinator-tooling/research/R1-findings.md`. No client
build is involved.

Build:
1. `tools/orchestration/retro.py` (ours, 227 lines). Add per-response list $ using R's price table
   and cost function (`R/tools/orchestration/orch/transcripts.py:31-38`; take only what is needed).
   Add these metrics: `cost.total_usd`, `cost.coordinator_usd` and its share, `cost.per_agent_usd`,
   `instructions.*_tokens` (AGENTS.md, CLAUDE.md, the role files, the skill), and
   `waste.budget_overruns_1x/2x` (from the `Budget:`/`budget <N> min` line of the brief the agent
   was spawned with, when one can be found; otherwise list it in `unavailable`). Every row also
   carries `head` (the git sha) and `unavailable` {metric: reason}. A model missing from the price
   table goes in `unavailable`; never guess a price. Keep the existing keys and CLI.
2. `tools/hooks/log_usage.py`: port R's. It appends `{at, weekly, weekly_resets_at, five_hour}` to
   `.agent-ledger/usage-readings.jsonl`, never blocks, and exits 0 on bad input.
3. `tools/hooks/subagent_stop.py`: port R's. It appends to `.agent-ledger/stops.jsonl` and saves the
   full last message to `.agent-ledger/reports/<agent_id>.md`. No worktree logic.
4. `tools/orchestration/progress.py`: a short block of about 10 lines.
   - A feature is any `specs/*/tasks.md` or `research/knowledge-graph/specs/*/tasks.md` without
     `**Status: done**`. For each, print its done and open `- [x]`/`- [ ]` counts.
   - Spend for the feature's window, via retro.py's functions. The window starts at the first
     commit touching the folder; `--since` overrides it.
   - The newest usage reading, and the coordinator's context: the last main-session response's
     tokens and $/turn, as in R's `context_size.py`.
5. `tools/orchestration/section.py`: copy R's, adjusted only for paths.
6. Tests next to each file, in the style of `tools/hooks/*_test.py`. Use fixture transcripts that
   you write yourself; never real ones.

Owns: tools/orchestration/**, tools/hooks/{log_usage,subagent_stop}.py and their tests,
tools/check.sh only if a new test file needs registering.
Others own (refused; propose text in your receipt instead): .claude/** (I register the hooks in
settings.json), specs/**, AGENTS.md, CLAUDE.md.
Never touch: client/, packets/, research/**, plan/, and every dirty path that `git status --short
-- tools specs .claude` does not show.

Done: the focused tests pass; `bash tools/check.sh --since <base>`; run `retro.py` and
`progress.py` against the real `~/.claude/projects/D--ddon-data/` transcripts, read-only, and put
their output (bounded) in the receipt; signed commits with explicit paths; then the receipt. In the
receipt, propose the settings.json entries for both hooks.
Stop: budget 90 min. Ask if R's code needs a worktree or Rust assumption you cannot drop cleanly.
Base: <filled by coordinator>. Commit trailer: Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
