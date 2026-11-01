Orchestration port: learnings from C:\ddon-dwarf-reconstructor-rust since 2026-10-17

Question/objective: which of the reconstructor's orchestration and role-definition changes since
2026-10-17 (148 commits touch `.claude/agents`, `.claude/skills`, `specs/orchestration.md`,
`docs/`, `AGENTS.md`, `CLAUDE.md` there) should ddon-data adopt, and how. ddon-data's current
versions: `specs/orchestration.md`, `.claude/skills/coordinate/SKILL.md`, `.claude/agents/*.md`
(implementer, reviewer, adversarial-reviewer, repository-researcher, evidence-researcher,
evidence-researcher-ida), `AGENTS.md` "Agents and coordination", `tools/hooks/`.

Read in the reconstructor (you have Read/Glob/Grep only; the coordinator lists the commits for
you below if needed): the current `specs/orchestration.md`, `.claude/skills/coordinate/` and `progress/`,
`.claude/agents/*.md` (the base roles, the generated `*-ida` variants and how
`cargo xtask ida-variants` makes them, `scribe`, `editor`, `planner`), `specs/performance-learnings/`,
and any learnings or retrospective notes those reference. Diff each against ddon-data's
counterpart.

Report, per finding: what changed there (commit, file, one-line quote), the problem it solved
(their evidence), whether ddon-data has the same problem (cite our file or ledger), and a
recommendation: adopt as is / adapt (say how) / skip (why). Rank by expected benefit.

Constraints that already decide some findings, do not recommend against them:
- ddon-data has no worktrees and runs one subagent at a time (Sam, 2026-10-17).
- Subagents run Opus 5.5 at **medium** effort; role files pin `effort: medium` (Sam,
  2026-11-01). The reconstructor's roles say `effort: high`: skip that part.
- Headless ida-mcp runs per agent on a private database copy (`research/ida/private-copy.sh`,
  hook `guard_ida`), ported 2026-11-01 from the reconstructor's `*-ida` roles.
- The coordinator keeps its context small: role agents do research, edits and runs.

Owns: nothing; read-only in both repositories. Your final message is the report (at most 120
lines); the coordinator files it as `specs/002-coordinator-tooling/research/orchestration-port-2026-11.md`.
Done: ranked findings, each with its source file and line.
Stop: budget 40 min.
