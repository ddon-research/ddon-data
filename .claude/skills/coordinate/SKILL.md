---
name: coordinate
description: The main session's checklist for running role agents in ddon-data (shared checkout, no worktrees) - resuming, writing briefs, spawning implementers, reviewers and researchers, landing a package from its receipt, auditing an agent's tool use, the context check and the efficiency retrospective. Use at session start when work will be delegated, and whenever a role agent reports.
---

# Coordinating role agents in ddon-data

The protocol is `specs/orchestration.md`; this is its checklist. Role agents never load it.

## Resume

1. The active feature: root `.specify/feature.json` or `research/knowledge-graph/specs/STATUS.md`;
   its `tasks.md` holds package state, running agents and the next step. Read `git status --short`
   with a pathspec outside `client/`/`packets/` before anything: other work is dirty in this tree.
2. Read the plan usage (`get_usage`, weekly window). From 90%: no new implementer. From 95%: wrap
   up running agents and work alone.

## Before spawning

- Is the work worth an agent? A fact a few tool calls can find, or a change touching files another
  package owns, stays with you.
- Is the request clear? If an answer would change what is built, regenerated, deleted or deployed,
  ask the user; otherwise pick the default, say so in the reply and in `tasks.md`.
- Pick the role: `implementer` (code or scripts, **one at a time**, main checkout),
  `adversarial-reviewer` (one risk, canaries in `.agent-ledger/canaries/`), `reviewer` (read-only,
  give it the git receipt), `repository-researcher`, `evidence-researcher` (read-only IDA). Not the
  built-in Explore/Plan/general-purpose types for project work: they carry no guards or receipts.
- **No `isolation: worktree` and no `effort`** on any spawn: ddon-data has no worktrees, and agents
  inherit the session's effort (Sam: medium).
- Work in another repository (ddon-hook, the reconstructor) uses that repository's roles,
  worktrees and guards: run it from a session started there.
- New or changed role files load only in a new session; commit them first.

## The brief (orchestration section 3), in `specs/<feature>/briefs/`

```
<feature> <package>: <title>
Question/objective: ... (build: 03040008 | 02030004 | PS4_02020005)
Owns: <globs>. Others own: <globs>. Never touch: <dirty paths of other work>, client/, packets/ data.
Source boundary: <files, IDB path, external docs>.
Done: <checks>; end with the receipt (role file).
Stop: budget <N> min; stop and ask if <decision>.
Base: <sha>. Commit trailer: <Co-Authored-By line>.
```

Quote the rule the agent needs; don't send it to read a large spec file whole.

## While an implementer runs

Commit nothing outside `specs/*/tasks.md` (its receipt covers `base..HEAD`); keep running-agent
records uncommitted until it lands.

## When an agent reports

1. Read the receipt only. For an implementer: `git log --format='%h %G? %s' <base>..HEAD` matches
   it (the Stop hook already compared branch, head, commits, signatures and its files' status); the
   gates are the brief's and `not run` lines are explained.
2. Risky work (decryption or key search, extraction or regeneration of evidence, scripts that
   delete, a guard, provenance and hashes): spawn an `adversarial-reviewer` with one named risk,
   30 minutes. Reproduce its canaries yourself before routing them.
3. Land: `bash tools/check.sh --since <base>` (background; wait for the notification, don't poll),
   record in `tasks.md` (package, commits, gate lines), commit the records.
4. Audit the agent's tool use: `python -X utf8 -I tools/orchestration/retro.py --since <its spawn time> --label "<package>"`,
   and, for a spawn whose settings matter (effort, model), its transcript's metadata:
   `jq -c . ~/.claude/projects/D--ddon-data/<session>/subagents/agent-<id>.meta.json` and
   `rg -o -m 3 '"perTurnEffort":"[a-z]+"' <its .jsonl>`. A repeated failure or refusal class
   becomes a guard case with a test, a script, or a brief change.

## Context check

`tools/hooks/context_watch.py` adds one reminder as the main session crosses 300k, 500k, 700k,
850k and 930k tokens. At the next natural break (a landing, a milestone) commit the records
(tasks.md: running agents with ids, next step), then ask the user to run `/compact`. Prefer a fresh
agent with a handoff over resuming one whose context is large.

## Milestone end

Run the efficiency retrospective (orchestration section 8): `retro.py --append --out`, read the
outliers and the instruction files, fix mechanical waste at once, replace stale instruction text,
record findings and target metrics in the feature.
