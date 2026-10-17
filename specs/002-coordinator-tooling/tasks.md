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

- [x] P1 `implementer`: cost and usage tooling (R1 gaps 1, 2, 3, 5, 8). Brief `briefs/P1-cost-tooling.md`.
      Commit 33b0bc5 (signed), 8 min, 43 tool calls, 123k tokens. Focused tests 14 + 10 OK. Gate
      (coordinator): `check.sh --since 1ed7f1e`: hooks passed (26 + 14), shell passed, flags and kg
      not run (no change). The worker's own run failed kg on the untracked, other-owned
      `research/knowledge-graph/`. Fix: `check.sh --since` now counts only `<rev>..HEAD`.
      Its first real readings (2026-10-17 transcripts): $54.57 in all, the coordinator $37.18 (68%);
      6 of 13 agents had no findable budget.
  - `retro.py` gains list $ per response, the coordinator's share, instruction tokens, budget
    overruns, `head` and `unavailable`.
  - Ported: `log_usage.py` and `subagent_stop.py` (output to `.agent-ledger/`), `progress.py`,
    `section.py`, with tests.
- [x] P2 `implementer`: `session_state.py` without worktrees (R1 gap 7). Commit 2111f3b (signed),
      3.6 min, 20 tool calls, 69k tokens. Focused tests 7 OK; worker gate `check.sh --since f5d102f`:
      hooks passed (33 + 14), flags and kg not run (no change). Dry runs of all three modes are in its
      receipt. The coordinator registered SessionStart, PreCompact and SubagentStart. The
      SubagentStop record has fired (`.agent-ledger/stops.jsonl`, `reports/<id>.md`).
- [ ] T004 Coordinator: register the P1/P2 hooks in `.claude/settings.json` (P1's two and P2's three: done); write the first row
      of `specs/efficiency-ledger.jsonl` (the baseline: 009 fix wave and this feature).
- [ ] T005 Coordinator: `.claude/rules/` with `paths:` scoping (R1 gap 9); move domain learnings
      out of `CLAUDE.md` when a spec closes.
- [ ] T006 ddon-hook: the same mechanisms, handed to that repository's coordinator (session
      local_3b681044) on 2026-10-17 at 9a4a55b. The list covers the text sections 0/8/9/10,
      autoCompactWindow, retro.py with $, progress, section, log_usage, subagent_stop and
      session_state, the settings registrations and the check.sh `--since` fix. Sam's rule (2026-10-17):
      ddon-hook's coordinator runs **at most one subagent at a time**, and every later setup change
      here is ported there. Done when its commits land and its first ledger row exists; verify them.

Not ported (R1 section d): the worktree, train and golden machinery; `receipt.py --verify`; the
pipeline metrics; the structure tools; `effort`; the concurrency setting.

## Closing (orchestration section 10)

- [ ] C1 `check.sh --all`; adversarial review of the new hooks; docs (`AGENTS.md` "Agents and
      coordination"); light retrospective; `**Status: done**`.

## Running

- (none)
