---
name: coordinate
description: The main session's checklist for running role agents in ddon-data (shared checkout, no worktrees) - resuming, writing briefs, spawning implementers, reviewers and researchers, landing a package from its receipt, auditing an agent's tool use, the context check and the efficiency retrospective. Use at session start when work will be delegated, and whenever a role agent reports.
---

# Coordinating role agents in ddon-data

The protocol is `specs/orchestration.md`; this is its checklist. Role agents never load it.

**The goal is the spec's completion.** Loop Sam in only on big decisions: push, merge to `main`,
deploy, launching the game, regenerating `client/` or `generated/`, scope changes, deleting
evidence. Decide everything else, record the choice in `tasks.md`, and keep going. After each
landing, tick the tasks, then plan and start the next wave. End a turn only when blocked on Sam or
on budget, and say exactly what is needed. A side session's brief names the spec's completion as
its goal, not one wave. A finished spec stays finished: new work on its output is a package of the
active spec.

Sub-coordinators (ddon-hook) bring their decisions here, not to Sam (Sam, 2026-10-17). Decide the
routine ones and escalate the big decisions above. One exception: a session's own config
(`.claude/**`, `AGENTS.md`, hooks, role files) needs Sam's approval in that session itself, because
a relayed approval does not count there. So the sub-coordinator sends the patch path to the
coordinator, which reviews it, applies it in that repository and commits it (Sam, 2026-10-17:
"Why is it asking for trivial change approval?"). Sam is asked only when the patch loosens a guard,
a permission or a deny rule.

## Resume

1. The active feature: root `.specify/feature.json` or `research/knowledge-graph/specs/STATUS.md`;
   its `tasks.md` holds package state, running agents and the next step. Read `git status --short`
   with a pathspec outside `client/`/`packets/` before anything: other work is dirty in this tree.
2. Read the plan usage (`get_usage`, weekly window). From 90%: no new implementer. From 95%: wrap
   up running agents and work alone.

## Before spawning

- **One subagent at a time, of any role** (Sam, 2026-10-17). Is one running? Then land or close it
  first. Sub-coordinator sessions (ddon-hook) follow the same cap.
- You write no code, tests or tooling: every such change, however small, goes to a role agent with
  a short brief. The one exception is a fix of a few lines that unblocks a landing already under
  way; run its tests before committing. A fact a few tool calls can find stays with you.
- Is the request clear? If an answer would change what is built, regenerated, deleted or deployed,
  ask the user; otherwise pick the default, say so in the reply and in `tasks.md`.
- Pick the role: `implementer` (code or scripts, main checkout),
  `adversarial-reviewer` (one risk, canaries in `.agent-ledger/canaries/`), `reviewer` (read-only,
  give it the git receipt), `repository-researcher` (writes its report under `specs/*/research/`),
  `evidence-researcher-ida` (ida-mcp on a private IDA copy; report under `specs/*/research/`),
  `evidence-researcher` (ida-assist, read-only). Not the built-in Explore/Plan types, and
  `general-purpose` only as "Your role is ..." for a role file not loaded yet: `agent_cap.py check`
  refuses the rest.
- The description is the title `<role> · <spec> <package>: <what>`
  (`implementer · 002 P4: reconstructor-port wave 2`); `agent_cap.py check` refuses another form.
- **No `isolation: worktree` and no `effort`** on any spawn: ddon-data has no worktrees, and every
  role file sets `model: inherit` and `effort: medium` (Sam, 2026-11-01).
- Work in another repository (ddon-hook, the reconstructor) uses that repository's roles,
  worktrees and guards: run it from a session started there.
- New or changed role files load only in a new session; commit them first.

## The brief (orchestration section 3): a new file per package in `specs/<feature>/briefs/`

```
<feature> <package>: <title>
Question/objective: ... (build: 03040008 | 02030004 | PS4_02020005)
Owns: <globs>. Others own: <globs>. Never touch: <dirty paths of other work>, client/, packets/ data.
Source boundary: <files, IDB path, external docs>.
Libraries: <existing deps to use>; own code only where no library fits, reason in the receipt.
Done: <checks>; end with the receipt (role file).
Stop: budget <N> min of work time; stop and ask if <decision>.
Base: <sha>. Commit trailer: <Co-Authored-By line>.
```

Quote the rule the agent needs; don't send it to read a large spec file whole. The agent gets your
loaded copy of AGENTS.md and CLAUDE.md, not the file on disk: after editing either, quote the changed
rule in every brief until the next compaction. No shell recipes the role file covers. Frame an
adversarial brief as research (the claim to falsify): a safety-classifier stop ends it with nothing.

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
4. For an agent past its work-time budget or 300k context, audit its tool use:
   `python -X utf8 -I tools/orchestration/retro.py --since <its spawn time> --label "<package>"`,
   and, for a spawn whose settings matter (effort, model), its transcript's metadata:
   `jq -c . ~/.claude/projects/D--ddon-data/<session>/subagents/agent-<id>.meta.json` and
   `rg -o -m 3 '"perTurnEffort":"[a-z]+"' <its .jsonl>`. A repeated failure or refusal class
   becomes a guard case with a test, a script, or a brief change.

## Context check

The session compacts itself at its 550k window (`autoCompactWindow` in the gitignored
`.claude/settings.local.json`, Sam, 2026-11-01). **Never ask the user to run `/compact`**: a manual
one throws away the prompt cache. `tools/hooks/context_watch.py` adds one reminder as the context
crosses 450k, 500k and 530k tokens; from the first, commit the records (tasks.md: running agents with
ids, next step) at each natural break (a landing, a milestone). Resume an agent only below about 300k
tokens and within 55 minutes of its last turn; past either, spawn a fresh one with a handoff.

## Reporting (orchestration section 9)

Every landing and wave end: start the message with `python -X utf8 -I tools/orchestration/progress.py`
(tasks done/open, spend, plan usage, context). Call `get_usage` first, which logs the reading. Then
what landed, the inefficiencies found and what was done, and what is next. Any decision for Sam goes
last, as one question.

## Wave end

Light retrospective: `retro.py --since <wave start> --label "<feature> W<n>" --append`; a metric past
its threshold against the previous ledger row is a finding. Then plan the next wave.

## A spec's end (orchestration section 10)

Add these as the spec's closing tasks and run them in order:
1. `check.sh --all`.
2. A whole-spec review, plus an adversarial review of the spec's new guards.
3. A docs audit (pages under `docs/` the spec touched; the `editor` role), then the fixes.
4. The full retrospective with a researcher on the outliers, the trajectories and the instructions.
5. Learnings placed and recorded.
6. `**Status: done**`.

Push and `main` wait for Sam.
