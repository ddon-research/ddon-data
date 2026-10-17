orch R1: what the reconstructor's agentic setup does that ddon-data's lacks

Question/objective: Map the coordinator behaviours of C:\ddon-dwarf-reconstructor-rust that the
ddon-data setup (commit 65c778c) is missing. The user named these gaps: reporting spend, plan
usage, inefficiencies and spec progress to the user; a retrospective at the end of each spec that
analyses subagent trajectories and tool usage; and, at spec end, required documentation updates and
derived learnings. Cost efficiency is the goal: for every mechanism, say what it costs and what
it saves. (No client build involved; this is tooling.)

Answer these, citing `path:line` for each claim and marking each mechanism as code-enforced (hook,
script, test) or text only (instruction):
1. Spend and usage: what is measured (tokens, turns, tool calls, wall-clock, plan windows, context)
   and by which script (tools/orchestration/efficiency.py, context_report.py, context_growth.py,
   context_size.py, tools/hooks/log_usage.py, session_state.py), when it runs, where it is stored
   (specs/efficiency-ledger.jsonl schema), and what the coordinator reports to the user, and when.
2. Progress: how spec and package progress is kept and surfaced (tasks.md conventions, dashboards,
   receipts, subagent_stop.py).
3. Spec end: the retrospective procedure (specs/efficiency-retrospectives/: read one or two for
   the format), how subagent transcripts and tool usage are analysed (which scripts, which fields),
   the documentation-update and learnings requirements (specs/architecture-learnings/,
   specs/performance-learnings/, the constitution in .specify/memory/, speckit-converge,
   .claude/rules/), and what closes a spec.
4. Cost controls: per-role model, maxTurns, budgets, usage thresholds, context thresholds,
   handoffs, and the rules that keep briefs and results small.
5. Anything else in .claude/ (settings.json hooks, rules/, skills/coordinate/, agents/),
   specs/orchestration.md, AGENTS.md or CLAUDE.md that the coordinator does and we do not.

Ours, for the comparison: D:\ddon-data\specs\orchestration.md, .claude/skills/coordinate/SKILL.md,
.claude/agents/*.md, .claude/settings.json, tools/hooks/{guard_bash,guard_paths,guard_read,log_tool,
context_watch,receipt}.py, tools/orchestration/retro.py, tools/check.sh.

Source boundary: read only. Under the reconstructor read .claude/, specs/orchestration.md,
specs/*-learnings/, specs/efficiency-retrospectives/, specs/efficiency-ledger.jsonl (first lines
only), .specify/memory/, tools/hooks/, tools/orchestration/, AGENTS.md, CLAUDE.md, and one or two
closed specs' tasks.md and closing sections. Never read target/, output_*, reports/, site/,
.cache/, .tmp/ or node_modules/. Read large files in ranges.
Constraints that stay: ddon-data has no worktrees (one writer at a time); agents set no effort
(they inherit Medium); the reconstructor's high/xhigh effort rules do not apply.

Done: a report of at most 150 lines: (a) a table of mechanism | where | enforced or text | what it
does | ours: have / partial / missing; (b) the spec-end procedure as an ordered checklist; (c) the
five to ten gaps worth porting, ranked by benefit per cost, each with the files to port and the
adaptation for no-worktrees; (d) what not to port, and why.
Stop: budget 45 min. If a mechanism depends on worktrees or the Rust workspace only, say so and move
on.
