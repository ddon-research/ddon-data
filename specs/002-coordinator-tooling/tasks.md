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

- [x] T008 `receipt.py` Stop hook: let a stop through with live background tasks, or a message of at
      most 3 lines whose first line starts `waiting:` / `blocked:`; tests; one line in
      `implementer.md` (F1).
- [x] T009 Text: the coordinator writes no code, tests or tooling (one exception: a few lines that
      unblock a landing in progress); replace `orchestration.md:29` and `SKILL.md:37-38` (F2).
- [x] T010 Settings, needs Sam's approval: `autoCompactWindow` for the main session and
      `subagentPromptCacheTtl: "1h"`; replace the skill's `/compact` request with commit-at-breaks;
      recalibrate `context_watch.py` (F3). Sam approved 2026-11-01; the keys live in the gitignored
      `.claude/settings.local.json` (550000, "1h"); P4 set the thresholds to 450k/500k/530k.
- [x] T011 Text: resume an agent only below ~300k tokens and within 55 min of its last turn, else
      respawn with a handoff (F4); budgets are work time, and past 300k context an agent commits and
      hands off `cut short:` (F5).
- [x] T012 `agent_cap.py check`: role allowlist and description format
      `<role> · <spec> <package>: <what>`, with tests (F6).
- [x] T013 `repository-researcher`: Write limited to `specs/*/research/*` by a `guard_paths` hook,
      Bash under `guard_bash`; report path + short summary as its final message (F7).
- [ ] T014 `evidence-researcher-ida`: `guard_paths` hook on Write; deny `close_database` in
      settings; a `check.sh` test that the ida-mcp plugin path exists; decide on the ida-assist
      `evidence-researcher` role (F8). Done in P4: the hook and the check.sh `mcp` line; the
      coordinator added the `close_database` deny to `.claude/settings.json`. Open: the ida-assist
      decision (P4 found no ida-assist server registered: `claude mcp list` shows only `ida`).
- [x] T018 `agent_cap.py`: a finished agent stays in `.agent-ledger/running/` (2026-11-01, twice:
      005 P3 and 002 P4 had to be deleted by hand before the next spawn); clear the entry when the
      agent's completion notification fires (SubagentStop), with a test.
- [x] T019 `receipt.py --print` fails with WinError 206 on a commit touching 110,065 paths (005 P3's
      JSON commit 5ce0ff6988): it passes every path to `git status`; use a pathspec file or batches.
      The same agent was resumed by its own background task's completion after its ledger entry was
      deleted (see T018), so two agents ran at once for a few minutes.
- [x] T020 Rule + guard: stage owned folders as directory pathspecs, never hundreds of thousands of
      literal paths (005 P6, 2026-11-01: `git add --pathspec-from-file` with ~290k paths ran 45 min,
      quadratic pathspec matching against 437k index entries; killed and redone with two folder
      pathspecs refused by the blanket-staging guard, so `git update-index --add --remove -z
      --stdin` from the path list: 44 s). The guard needs an allowed form for folders an agent owns.
      Repository tuning (Sam approved, applied by the coordinator in `.git/config`):
      `feature.manyFiles` (index v4 + skipHash: index 89.3 -> 61.2 MB; `git status -uno` 172 ->
      136 ms, with untracked 412 -> 294 ms, hyperfine 3 runs), `commitGraph.changedPaths` + a
      commit-graph rewrite with Bloom filters (`feature.manyFiles` reverted the same day: Sam's viewer
      showed every `client/` JSON as modified and many files untracked while git itself was clean,
      most likely a reader without index v4/skipHash support; now `index.skipHash false`, index v2;
      the reader was MSYS2's own `/usr/bin/git` (Cygwin build, no fsmonitor): it and Git for Windows
      record different stat fields, so each full-refreshed the 437k-entry index after the other
      (MSYS 54-105 s, GfW 9 s). `core.checkStat minimal` + `core.trustctime false` cut that to
      MSYS 7-22 s, GfW 0.8-2.4 s; Sam uses Git for Windows only from now on); `git repack -d` packed the loose objects (141,809 -> 1,020 unreachable leftovers, 70 s; `maintenance run --task=loose-objects` packed none). Sam approved T020's tuning on 2026-11-01.
- [ ] T022 T018 does not clear an agent whose earlier stops were `waiting:` with background tasks
      (2026-11-01, 006 T001c2 `a0f489bb719bbe4f0`: three `waiting:` stops, then a final receipt with
      `state: done`; its running record stayed and refused the next spawn as "running 0 min"; T001c's
      record also stayed). Clear on a final stop with no live background tasks, with a test.
- [ ] T021 Private IDA copies are never removed (2026-11-01: 10 `ddon-data-*` copies, ~7 GB, in
      `D:/research/DDON-binaries/IDA9.5/*/`; the coordinator stopped six orphaned `idat.exe` workers
      and deleted them). Cause: the ida-mcp server keeps one `idat.exe` per opened database alive
      after the agent ends, and `close_database` is denied. Fix: allow `mcp__ida__close_database`
      (guard_ida checks the path is a private copy; saving into a private copy is harmless); the
      `-ida` role closes its databases before its final message; `research/ida/private-copy.sh
      --remove <pc|ps4> <name>` deletes a closed copy; the coordinator runs it at landing (skill
      step) and `session_state.py` lists leftover copies and orphaned `idat.exe` workers.
- [x] T017 Guard: refuse `git commit` without a `-- <paths>` pathspec while the index holds staged
      paths of other work. P4's b204c9daad committed three files another session had staged (Sam
      approved the rewrite: soft reset to 1d0ab74e1a, the four commits remade with explicit paths
      as 010b1ee2f6, 3e81c269a4, cce5b04632, 0a384f100f; the three files are staged again)
      (`binaries/PS4_02020005/elf-dumps/ida/functions.ida-9.5.jsonl`,
      `research/external/Launch_DDO_NoAdmin.cmd`, `research/external/flag-smasher.csx`).
- [x] T015 Brief and skill text: quote changed AGENTS.md/CLAUDE.md rules in briefs until the next
      compaction; one new brief file per package; research framing for adversarial briefs; audit an
      agent past its work-time budget or 300k context (F10, F11, F12).
- [x] T016 Fix the contradictions R2 lists: `orchestration.md:49` and `SKILL.md:45-46` still say
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
