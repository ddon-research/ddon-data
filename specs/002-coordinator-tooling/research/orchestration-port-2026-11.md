Orchestration port report: what ddon-data should adopt from the reconstructor's changes since 2026-10-17

Scope and method. I read both repositories read-only. Reconstructor files: `specs/orchestration.md`, `.claude/skills/coordinate/SKILL.md`, the `.claude/agents/` files (implementer, researcher, researcher-ida, planner, editor, scribe), `xtask/src/ida_variants.rs`, `.claude/settings*.json`, `specs/performance-learnings/applied.md`, and the retrospective findings for specs 026, 029 and 030. ddon-data files: the counterparts named in the brief, `tools/hooks/{agent_cap,receipt}.py`, `.claude/settings.json`, `specs/efficiency-ledger.jsonl`, `specs/002-coordinator-tooling/research/retro-002-W1.md` and `.agent-ledger/tool-calls.jsonl`. I could not run git, so each commit hash comes from the subject lines in recon-orch-commits.txt (inferred). The line citations come from reading the files (verified). No client build applies: this is tooling only. I did not read `progress/` or `.claude/rules/guards.md`.

Ranked findings, highest expected benefit first

1. Short "waiting:" or "blocked:" stops get past the Stop hook (adopt; small Python change). Verified gap.
   - Reconstructor: retro-029-findings.md:127-148, F5. Their implementer.md:97 says "To wait ... end your turn with at most 3 lines, the first starting `waiting: <what>` (or `blocked: <why>`)."
   - The problem they had: 50 Stop-hook refusals. Agents ended a turn to wait, got refused, and pasted interim receipts. That gave 106 receipt notifications for 69 implementers.
   - ddon-data has the same problem. `tools/hooks/receipt.py:130-142` refuses every stop without a receipt; its only exemption is `stop_hook_active`. Yet `.claude/agents/implementer.md:60-61` and :75 say to run `check.sh` in the background and end the turn, and :47 says to end the turn to ask a question. Each of those stops is refused once.
   - Recommendation: in `check()`, let a stop through when `background_tasks` > 0, or when the message is at most 3 lines and its first line starts with `waiting:` or `blocked:`. Add tests, and add one line to implementer.md.

2. The coordinator writes no code (adapt). Verified contradiction.
   - Reconstructor: 239d380d, SKILL.md:29-33: "Every change to code, tests or tooling, however small, goes to a role agent with a short brief". The one exception is a fix of a few lines that unblocks a landing already under way.
   - The problem they had: each coordinator turn re-reads the whole context (about $0.08 a call at 400k), and the diffs then stay in context.
   - ddon-data has the same problem, and worse:
     - In retro-002-W1.md:21-22 the coordinator takes 66.4% of spend ($24.38 of $36.69).
     - The ledger shows the coordinator itself doing multi-line `sd` edits of tasks.md (line 108) and `cat agent_cap.py | head -120` (line 454).
     - Our own text contradicts the brief's constraint: `specs/orchestration.md:29` says "A small or coupled change stays with the coordinator", and `SKILL.md:37-38` keeps changes in other packages' files with the coordinator.
   - Recommendation: replace those two lines with the reconstructor's rule and its exception. Keep "a fact a few tool calls can find stays with you".

3. Context window and cache settings (adopt the settings and the text). Verified.
   - Reconstructor:
     - `settings.local.json:2` sets `"autoCompactWindow": 550000`.
     - `settings.json:275` sets `"subagentPromptCacheTtl": "1h"`.
     - 368f5725, SKILL.md:94: "Never ask the user to run `/compact` ... a manual one throws away the cache".
   - The problem they had: 539 coordinator responses above 500k ($67.49 of cache reads) before the 550k window (retro-026 F7).
   - ddon-data has the same problem. Neither key exists in `.claude/*.json` (Grep found nothing), and `main_peak_context` was 583,769 in W1. Our `SKILL.md:89-92` tells the coordinator to ask the user to `/compact`.
   - Recommendation:
     - Set both keys. They are a config change, so Sam must approve them in-session.
     - Replace the skill's context check: commit the records at each break, start that about 100k before the window, and never ask for `/compact`.
     - Recalibrate the `context_watch.py` thresholds (300k to 930k) to the window.

4. Resume or respawn, with numbers (adopt).
   - Reconstructor: 030 F1 (likely 7975587d), SKILL.md:59: resume "while it is below about 300k tokens and within 55 minutes of its last turn; past either limit, spawn a fresh one with a handoff". An agent that will wait longer commits, ends with `cut short:` and leaves a handoff.
   - The problem they had: 14 cache rewrites cost $30.37 after pauses of 72 to 249 minutes.
   - ddon-data has the same gap. `specs/orchestration.md:89-90` says only "while its context is small". The risk is the same with one agent at a time, since an agent waiting on Sam pays the same rewrite.
   - Recommendation: replace §5's bullet with the two limits.

5. Budget is work time, and context is not budget (adapt the text now; add the mechanism later).
   - Reconstructor: f6343839 and 026 F3, implementer.md:47,49: "Your budget is work time on the clock ... Context is not budget: past 300k tokens, commit and hand off with `cut short:`." Also 030 F2: time spent with the turn ended does not count.
   - The problem they had:
     - 16 implementers ended at 40 to 69 of 120 minutes.
     - "Budget overruns" were really waiting: P5 ran 9.0 h of wall time for 1.9 h of work.
     - 026 F3 also found that text alone did not hold. The fix there is a clock that `receipt record` prints.
   - ddon-data has the same wording: `implementer.md:23` says "90 minutes of wall clock", and `orchestration.md:66` says "wall-clock time". I found no evidence of early endings here (not measured).
   - Recommendation:
     - Change both texts to work time and add the 300k handoff line.
     - Optionally have `receipt.py --print` print `work time: N of M min`.
     - Change `retro.py` to count overruns on work time.

6. A spawn guard: role, title and committed brief (adapt into the `agent_cap.py check` mode).
   - Reconstructor: 05e1e692 and 20777846, SKILL.md:51-54. The `guard_agent` hook refuses a built-in or fork agent type, a description not in the form `<role> · <spec> <package>: <what>`, and a brief that is not committed.
   - The problem they had: `/usage` could not attribute agents.
   - ddon-data has the same problem:
     - W1 had 5 of 11 agents as general-purpose or Explore.
     - One description had no package ("Architecture and anti-debug review"), and `waste.budget_unknown` lists 2 agents (retro-002-W1.md:31-45).
     - `orchestration.md:69` states the rule as text only. `agent_cap.py:128-141` checks only the cap.
   - Recommendation:
     - Extend `check` with the role allowlist and the title regex, with tests.
     - Allow `general-purpose` only together with "Your role is ..." (the case in `orchestration.md:51-54`).
     - Leave out the committed-brief check: ddon-data commits records only after landing.

7. The researcher writes its own report and has Bash (adapt).
   - Reconstructor: `researcher.md:15,29` has Write and Edit limited by `guard_paths.py 'specs/*/research/*'`, plus Bash for measurement: "Write the report at the path your brief names ... nothing is left only there."
   - The problem they had: research agents with no role file (029 F13), and reports landing in the coordinator's context (029 F6).
   - ddon-data has the same problem. `repository-researcher.md:4` is `tools: Read, Glob, Grep`, so the coordinator must take this whole report into its context and file it, which is what this brief does. `orchestration.md:157-158` also asks that researcher for a "bounded `jq` over the transcripts", which it cannot run. That is a verified contradiction.
   - Recommendation:
     - Add Write with a PreToolUse `guard_paths.py 'specs/*/research/*'` hook, and Bash under `guard_bash`.
     - Keep the other bans (generators, builds, databases).
     - The final message becomes the path plus a summary of at most about 15 lines.

8. The `-ida` variant's safety and drift checks (adapt; skip the generator).
   - Reconstructor:
     - 76584ede, e9b8b650 and d7aa1951, `ida_variants.rs:1-24`: variants are generated from the base role plus one block. A test fails when a variant drifts from its base, and `doctor` flags a missing plugin path ("the plugin cache is versioned").
     - `researcher-ida.md:11-16` keeps the base's `guard_paths` Write hook, and both `save_database` and `close_database` are denied in settings.
   - ddon-data's state, verified:
     - `evidence-researcher-ida.md:10` grants Write with no hook. The limit at :43 ("Write is for that file only") is text only.
     - :17 hard-codes `.../ida-mcp/20261028.0.3`.
     - `settings.json:17` denies only `save_database`.
     - The base `evidence-researcher.md:4` still uses `mcp__ida-assist__*`. The reconstructor removed ida-assist from user scope (21ef76f0). Whether it is still registered for ddon-data was not checked; Grep found no ida-assist entry in our settings files.
   - Recommendation:
     - Add the `guard_paths` hook to the `-ida` file.
     - Add a test to `tools/check.sh` that the `mcpServers` project path exists.
     - Deny `mcp__ida__close_database` in settings.
     - Decide whether to retire the ida-assist role or rewrite it. A generator for one variant is not worth it.

9. Guards that rewrite the command instead of refusing (adapt selectively).
   - Reconstructor: 026 F2 and 030 F6. PreToolUse `updatedInput` rewrites the command instead of refusing it (add `-A` to a multi-line `sd -F` on LF files; drop a pipe after a gate). The problem they had: two-thirds of refusals were an agent's first contact with that rule, so the cost grows with the number of agents.
   - ddon-data has the same pattern on a small scale: 24 refusals in 1,338 logged calls, mostly multi-line `sd` and `cat | head`.
   - We also have a guard false positive. Ledger line 356 refused `type -a ccache | head -3` as `cat | head`.
   - ddon-data has CRLF files, so the `sd -A` rewrite must check for no CR first, as theirs does. Fixing the false positive is the cheaper first step.

10. Briefs (adopt as small text changes).
    - SKILL.md:61: an agent gets the coordinator's loaded copy of AGENTS.md and CLAUDE.md, not the file on disk. After editing either, quote the changed rule in every brief until the next compaction. This bears directly on today's medium-effort edit to AGENTS.md.
    - SKILL.md:48: a new brief file per package, never written over another.
    - SKILL.md:58 and 030 F5: no shell recipes the role file already covers, and the budget as one line.
    - SKILL.md:55,117: review briefs in research framing. A safety-classifier stop ends the agent with nothing (P4a2, "Attack"). This matters for ddon-data's adversarial reviews of decryption and anti-debug work.

11. A measured trigger for audits (adapt).
    - Reconstructor: 030 F7, SKILL.md:28. The "audit at each landing" instruction was followed 0 times in 030. It became: an agent past its work-time budget or past 300k context gets an audit.
    - ddon-data: `SKILL.md:81` and `orchestration.md:116-118` say "each landing". The ledger has 7 `retro.py` call lines in total (inferred: it is not run at every landing).
    - Recommendation: use the measured trigger.

12. Smaller items to adopt as single lines.
    - "A finished spec stays finished" (SKILL.md:18): new work on its output is a package of the active spec. Spec 001 is closed.
    - The coordinator's own tool code runs its tests before committing (SKILL.md:19).

Skip, with reasons
- Merge trains, `land start` and `land finish`, counter anchors, corpus slots, `cleanup.sh`, teardown and the disk gates: these need worktrees and parallel branches, which ddon-data rules out (Sam).
- Quiet windows and peer-session messaging (SKILL.md:22): these are for timed A/B runs, which ddon-data does not do.
- The port of Python tooling to Rust (7d9dc306, SKILL.md:127-131): ddon-data's tools are Python by design.
- `effort: high` for research and review roles (75c4137e, SKILL.md:61): the constraint in the brief decides this.
- The scribe role and agy routing (fb780466, 5cb95fcd): these are for writing LLM method bodies, and ddon-data has no such work.
- The planner role: it is built around their refusal census and layer table. Our briefs come from Spec Kit tasks.
- The editor role (`editor.md`, guard on `docs/*`): defer. ddon-data's docs step (`orchestration.md:153-155`) is small. Revisit if a spec's docs audit grows; ddon-hook already uses one.
- "A finished spec keeps no scripts" (d8a7e941, SKILL.md:133-138): in ddon-data, research scripts under `specs/` are provenance for the evidence (AGENTS.md "Evidence rules"). Deleting them needs Sam.

Contradictions inside ddon-data, to fix on the way
- `specs/orchestration.md:49` and `SKILL.md:45-46` say role files and spawns set no `effort` and agents inherit the session's. AGENTS.md "Agents and coordination" and all six role files set `effort: medium` (verified). Both texts need replacing.
- `SKILL.md:42-43` lists 5 roles and does not mention `evidence-researcher-ida`.
- `orchestration.md:157-158` asks a role with no Bash to run `jq` (finding 7).
- `orchestration.md:29` and `SKILL.md:37-38` contradict the brief's "role agents do research, edits and runs" (finding 2).

Checks I did not run
- I did not use git in either repository (no Bash). The commit for each change is inferred from subject lines, and the "since 2026-10-17" scope comes from the coordinator's list.
- I did not read the subagent transcripts for interim-stop refusals in ddon-data. To measure finding 1, count Stop refusals in `.agent-ledger/stops.jsonl`.
- I did not check whether ida-assist is still registered for this project's user or local MCP scope.
- I did not check whether `context_watch.py`'s thresholds would conflict with a 550k window.
