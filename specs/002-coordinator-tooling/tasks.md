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
- [x] P3 `implementer`: `agent_cap.py` refuses a second concurrent subagent (Sam's cap, 2026-10-17;
      text in orchestration section 1, 67fc6b3). Brief `briefs/P3-agent-cap.md`. Commit ed9edfb
      (signed); 7 focused tests; `check.sh --since 67fc6b3`: hooks passed (40 + 14), flags and kg
      not run (no change). It held its tests through the quiet window as told. The coordinator
      registered check, start and stop.
- [x] T004 Coordinator: registered the P1, P2 and P3 hooks in `.claude/settings.json`. Wrote the
      first row of `specs/efficiency-ledger.jsonl`: "002 W1 (baseline)", since 16:00 on 2026-10-17;
      report `research/retro-002-W1.md`. It reads $36.69 in all, of which the coordinator $24.38
      (66.4%); 539 turns; refused 2.8%, failed 1.05%; budget overruns 0; 2 agents with no
      budget. Finding: most spend is the coordinator's per-turn cache reads, and a large share of
      its turns only relay side-session notes. Ruling: relay turns take one line and no tool calls;
      compact at milestones. Metric: `cost.coordinator_share_pct` below 50% in the next row.
- [ ] T007 `guard_bash.py` false positive: it reads Bash's `type -a X | head` as `cat | head`,
      because `type` is in READERS (it is Get-Content only in PowerShell). Treat `type` as a reader
      only for the PowerShell tool. Port the fix to ddon-hook.
- [ ] T005 Coordinator: `.claude/rules/` with `paths:` scoping (R1 gap 9); move domain learnings
      out of `CLAUDE.md` when a spec closes.
- [ ] T006 ddon-hook: the same mechanisms, handed to that repository's coordinator (session
      local_3b681044) on 2026-10-17 at 9a4a55b. The list covers the text sections 0/8/9/10,
      autoCompactWindow, retro.py with $, progress, section, log_usage, subagent_stop and
      session_state, the settings registrations and the check.sh `--since` fix. Sam's rule (2026-10-17):
      ddon-hook's coordinator runs **at most one subagent at a time**, and every later setup change
      here is ported there. Done when its commits land and its first ledger row exists; verify them.

### Wave 2: reconstructor learnings since 2026-10-17 (Sam, 2026-11-01)

Report `research/orchestration-port-2026-11.md` (R2, `repository-researcher`, medium effort,
4.7 min, 63 tool calls; findings ranked by benefit). Each item cites its finding number.

- [ ] T008 `receipt.py` Stop hook: let a stop through with live background tasks, or a message of at
      most 3 lines whose first line starts `waiting:` / `blocked:`; tests; one line in
      `implementer.md` (F1).
- [ ] T009 Text: the coordinator writes no code, tests or tooling (one exception: a few lines that
      unblock a landing in progress); replace `orchestration.md:29` and `SKILL.md:37-38` (F2).
- [ ] T010 Settings, needs Sam's approval: `autoCompactWindow` for the main session and
      `subagentPromptCacheTtl: "1h"`; replace the skill's `/compact` request with commit-at-breaks;
      recalibrate `context_watch.py` (F3).
- [ ] T011 Text: resume an agent only below ~300k tokens and within 55 min of its last turn, else
      respawn with a handoff (F4); budgets are work time, and past 300k context an agent commits and
      hands off `cut short:` (F5).
- [ ] T012 `agent_cap.py check`: role allowlist and description format
      `<role> · <spec> <package>: <what>`, with tests (F6).
- [ ] T013 `repository-researcher`: Write limited to `specs/*/research/*` by a `guard_paths` hook,
      Bash under `guard_bash`; report path + short summary as its final message (F7).
- [ ] T014 `evidence-researcher-ida`: `guard_paths` hook on Write; deny `close_database` in
      settings; a `check.sh` test that the ida-mcp plugin path exists; decide on the ida-assist
      `evidence-researcher` role (F8).
- [ ] T015 Brief and skill text: quote changed AGENTS.md/CLAUDE.md rules in briefs until the next
      compaction; one new brief file per package; research framing for adversarial briefs; audit an
      agent past its work-time budget or 300k context (F10, F11, F12).
- [ ] T016 Fix the contradictions R2 lists: `orchestration.md:49` and `SKILL.md:45-46` still say
      "no effort"; `SKILL.md:42-43` misses `evidence-researcher-ida`; `orchestration.md:157-158`
      asks a role without Bash for `jq`.
- T007 covers F9's false positive; F9's rewriting guards are deferred.

Not ported (R1 section d): the worktree, train and golden machinery; `receipt.py --verify`; the
pipeline metrics; the structure tools; `effort`; the concurrency setting.

## Closing (orchestration section 10)

- [ ] C1 `check.sh --all`; adversarial review of the new hooks; docs (`AGENTS.md` "Agents and
      coordination"); light retrospective; `**Status: done**`.

## Running

- (none)
