# 002 Coordinator tooling: spend, progress and spec-end mechanisms

A small feature, with no `spec.md`: it ports the reconstructor's cost and closing mechanisms
(`C:\ddon-dwarf-reconstructor-rust`, working tree as of 2026-10-17) to ddon-data. Sam asked for it on
2026-10-17: "report on spend, usage, inefficiencies, progress in specs ... a retro and analyzing
subagent trajectories and tool usage ... update documentation, derive learnings". The goal is the
setup's cost efficiency. Constraints: no worktrees here, one writer, no `effort` on spawns or role
files.

## Research

- [x] R1 `repository-researcher` (45 min budget; 4.2 min, 58 tool calls, 116k tokens): mapped the
      reconstructor's mechanisms against ours. Brief: `briefs/R1-reconstructor-setup.md`; findings:
      `research/R1-findings.md`.

## Coordinator text (done by the coordinator)

- [x] T001 Goal rule: the coordinator drives specs to completion and asks Sam only on big decisions
      (`specs/orchestration.md` section 0, coordinate skill; 1bd42cf).
- [x] T002 Reporting rule (orchestration section 9), wave-end light retro (section 8), spec-end
      procedure (section 10), skill sections to match.
- [x] T003 `autoCompactWindow: 400000` on all five role files (R1 gap 6).

## Packages

- [ ] P1 `implementer`: cost and usage tooling (R1 gaps 1, 2, 3, 5, 8). Brief `briefs/P1-cost-tooling.md`.
  - `retro.py` gains list $ per response, the coordinator's share, instruction tokens, budget
    overruns, `head` and `unavailable`.
  - Ported: `log_usage.py` and `subagent_stop.py` (output to `.agent-ledger/`), `progress.py`,
    `section.py`, with tests.
- [ ] P2 `implementer`: `session_state.py` without worktrees (R1 gap 7), after P1.
- [ ] T004 Coordinator: register the P1/P2 hooks in `.claude/settings.json`; write the first row
      of `specs/efficiency-ledger.jsonl` (the baseline: 009 fix wave and this feature).
- [ ] T005 Coordinator: `.claude/rules/` with `paths:` scoping (R1 gap 9); move domain learnings
      out of `CLAUDE.md` when a spec closes.
- [ ] T006 ddon-hook: the same mechanisms, handed to that repository's coordinator once P1/P2 land
      (its own roles and worktrees).

Not ported (R1 section d): the worktree, train and golden machinery; `receipt.py --verify`; the
pipeline metrics; the structure tools; `effort`; the concurrency setting.

## Closing (orchestration section 10)

- [ ] C1 `check.sh --all`; adversarial review of the new hooks; docs (`AGENTS.md` "Agents and
      coordination"); light retrospective; `**Status: done**`.

## Running

- (none)
