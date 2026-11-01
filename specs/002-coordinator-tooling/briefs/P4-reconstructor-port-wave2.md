002 P4: reconstructor-port wave 2 (hooks, role files, coordinator text)

Objective: apply spec 002 tasks T008, T009, T011-T016 from
`specs/002-coordinator-tooling/research/orchestration-port-2026-11.md` (read it first; finding
numbers F1-F12 below refer to it). Each finding names the reconstructor file and line to port
from (`C:/ddon-dwarf-reconstructor-rust`, read-only) and our file and line to change.

Do, in order (commit after each group, signed, explicit paths):
1. T008 (F1): `tools/hooks/receipt.py` Stop check lets a stop through when background tasks are live
   or the final message is at most 3 lines starting `waiting:` / `blocked:`; tests beside the
   existing ones; one line in `.claude/agents/implementer.md`.
2. T012 (F6): `tools/hooks/agent_cap.py check` also refuses a spawn whose `subagent_type` is not a
   role in `.claude/agents/` (allow `general-purpose` only when the prompt starts "Your role is")
   and whose description does not match `<role> · <spec> <package>: <what>`; tests. Do not require
   a committed brief.
3. T013 (F7), T014 (F8): `repository-researcher` gets Write guarded by a PreToolUse
   `guard_paths`-style hook limited to `specs/*/research/*` (port the reconstructor's
   `guard_paths.py` if ours has none) and Bash under the existing `guard_bash`; final message =
   report path + at most 15 lines. `evidence-researcher-ida` gets the same Write guard for
   `specs/*/research/*`. Add a `tools/check.sh` test that the ida-mcp project path in
   `evidence-researcher-ida.md` exists. Report (do not decide) whether the ida-assist
   `evidence-researcher` role still has a registered server.
4. Text (T009 F2, T011 F4/F5, T015 F10-F12, T016): edit `specs/orchestration.md`,
   `.claude/skills/coordinate/SKILL.md`, `.claude/agents/implementer.md` as the findings say. Keep
   ddon-data's rules: no worktrees, one subagent at a time, `effort: medium` on every role file
   (Sam, 2026-11-01; AGENTS.md "Agents and coordination" already says so: the "no effort" text in
   `orchestration.md:49` and `SKILL.md:45-46` is the stale part).
Not in this package: T010 (settings: `autoCompactWindow`, `subagentPromptCacheTtl`, the `/compact`
text, `context_watch.py`), which waits for Sam's approval; F9's rewriting guards; T007.

Owns: `tools/hooks/receipt.py`, `tools/hooks/agent_cap.py`, a new `tools/hooks/guard_paths.py`,
their tests, `tools/check.sh`, `.claude/agents/*.md`, `specs/orchestration.md`,
`.claude/skills/coordinate/SKILL.md`, `specs/002-coordinator-tooling/tasks.md` (tick your tasks).
`.claude/settings.json` only to register the new hook entries (no other key). Never touch:
packets/ (a background ImHex export is writing `packets/decrypted_json`), client/, research/,
other specs, other uncommitted files (many belong to other work: stage only your paths).
Libraries: the standard library and the hooks' existing helpers; no new dependencies.
Done: commits; `bash tools/check.sh --since <base>` passing; a receipt listing each task with its
commit, test counts, and what was left.
Stop: budget 60 min of work. Stop and report if a hook change would block the coordinator's own
spawns in a way the tests cannot cover.
Base: 0688ab37c4.
