002 P2: session_state.py, the coordinator's state across a compaction

Objective: after a compaction or resume, the coordinator gets its state injected instead of
re-deriving it. Subagents spawned after an instruction file changed get a diff of that change. Port
`C:\ddon-dwarf-reconstructor-rust\tools/hooks/session_state.py` (224 lines, with its test; read-only)
and adapt it to ddon-data, which has one checkout and no worktrees or trains. No client build is
involved.

Modes (one script, one mode per hook event):
- `start` (SessionStart, main session only; a subagent is a call whose input carries `agent_id`):
  - Records the hash and text of AGENTS.md, CLAUDE.md and ~/.claude/CLAUDE.md in
    `.agent-ledger/loaded-instructions.json`.
  - On source `compact` or `resume`, returns as `additionalContext`:
    - `tools/orchestration/progress.py`'s block;
    - the `## Running` and the last `Next:` lines of each active feature's `tasks.md`;
    - `git status --short -- tools specs .claude` (bounded; never client/ or packets/).
  - Drop the worktree and train parts.
- `precompact` (PreCompact, main session only): copies `<scratchpad>/briefs/*.md` into the
  active feature's `briefs/` when no file of that name exists there. Copy only; never delete.
- `subagent` (SubagentStart): when an instruction file differs from the recorded copy, returns the
  unified diff, capped at about 12k characters.
- Every failure exits 0 silently. `HOOK_ROOT`, `HOOK_HOME` and `HOOK_SCRATCHPAD` stand in for the
  paths in tests. Reuse `progress.py`'s feature discovery; don't copy it.

Owns: tools/hooks/session_state.py, tools/hooks/test_session_state.py.
Others own: .claude/** (I register the hooks), specs/**, AGENTS.md, CLAUDE.md, the rest of tools/.
Never touch: client/, packets/, research/**, plan/, other dirty paths.

Done:
- focused tests pass;
- `bash tools/check.sh --since <base>`;
- a dry run of each mode with a hand-written stdin JSON, outputs bounded and in the receipt;
- signed commit with explicit paths;
- the receipt, with the proposed settings.json entries for SessionStart, PreCompact and
  SubagentStart.

Stop: budget 60 min.
Quiet windows: if the coordinator tells you a quiet window is on, run no tests or gates until it says
it is over; reading and editing are fine.
Base: given in the spawn prompt. Commit trailer: Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
