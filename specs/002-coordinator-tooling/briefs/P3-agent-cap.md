002 P3: enforce one subagent at a time with a hook

Objective: Sam's rule (2026-10-17) allows at most one subagent of any role at a time. Today it is
text in `specs/orchestration.md` section 1; make a hook refuse a second spawn. No client build is
involved.

Build `tools/hooks/agent_cap.py`, one script with one mode per hook event:
- `start` (SubagentStart): write `.agent-ledger/running/<agent_id>.json` with `{agent_id, agent_type,
  started}`.
- `stop` (SubagentStop): remove that file, unless the input shows the agent still has background
  work (`background_tasks` > 0, as `subagent_stop.py` reads it): it will resume, so it still counts
  as running.
- `check` (PreToolUse on `Agent`): if any running file is younger than 4 h, refuse (exit 2, the
  message on stderr). Name the running agent, its type and its age, and say: "one subagent at a
  time (orchestration section 1): land or stop it first, or resume it with SendMessage". Ignore
  files older than 4 h and delete them as stale. `SendMessage` is never refused.
- Unparseable input exits 0 (never block on a hook bug), except that `check` refuses only on a
  clear running record.
- Follow `tools/hooks/hooklib.py` and the existing hooks' style. `HOOK_ROOT` or the ledger override
  stands in for the paths in tests.

Tests in `tools/hooks/test_agent_cap.py` cover: start then check refuses; stop then check allows;
stop with background work still refuses; a stale file is ignored and removed; bad input exits 0.

Owns: tools/hooks/agent_cap.py, tools/hooks/test_agent_cap.py.
Others own: .claude/** (I register the hooks), specs/**, AGENTS.md, CLAUDE.md, the rest of tools/.
Never touch: client/, packets/, research/**, plan/, other dirty paths.

Done:
- focused tests;
- `bash tools/check.sh --since <base>` (hold it if I announce a quiet window);
- a signed commit with explicit paths;
- a receipt with the proposed settings.json entries.

Stop: budget 45 min.
Base: given in the spawn prompt. Commit trailer: Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
