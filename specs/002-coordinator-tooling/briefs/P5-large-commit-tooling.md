002 P5: receipt, ledger and staging tooling for large commits (T017-T020)

Objective: make the coordination hooks work for packages that commit 1,000-260,000 files (spec 005
regenerated packet JSON). Evidence: every implementer since 005 P3 wrote its receipt by hand.

Do (tests beside the existing hook tests; commit per item):
1. T019 `tools/hooks/receipt.py:60` passes every touched path to `git status --porcelain -- <paths>`
   and fails with WinError 206 above ~32k characters. Run `git status --porcelain -z` once without
   pathspecs (fsmonitor makes it ~0.3 s here) and filter by the touched set in Python; never pass
   path lists on the command line or as `--pathspec-from-file` (quadratic against the 437k-entry
   index: 005 P6's add ran 45 min). Same for any other git call in the hooks that takes path lists
   (`rg -n 'subprocess|git' tools/hooks/*.py`). Test with a synthetic list of 200,000 touched paths.
2. T018 `tools/hooks/agent_cap.py`: clear the agent's `.agent-ledger/running/<id>.json` when it
   finishes (SubagentStop hook, or on the next `check` when the transcript shows the agent ended);
   twice the coordinator had to delete entries by hand.
3. T020 `guard_bash.py`: allow staging folders the brief owns as directory pathspecs
   (`git add -- <dir> <dir>`, at most a handful) instead of refusing them as blanket staging; keep
   refusing `git add -A`/`.`/`*` and bare `git add -u`; refuse `--pathspec-from-file` with a pointer
   to `git update-index --add --remove -z --stdin`.
4. T017 `guard_bash.py`: refuse a bare `git commit` (no `-- <paths>`) while the index holds staged
   paths the agent did not stage (compare `git diff --cached --name-only` with the brief's owned
   globs if available, else require `--`).
5. One line each in `.claude/agents/implementer.md` and `specs/orchestration.md` for 3 and 4 (as
   proposed text in your receipt if the guard refuses you those files).

Owns: `tools/hooks/{receipt,agent_cap,guard_bash}.py`, their tests, `tools/check.sh` if a test needs
registering, `.claude/settings.json` only to register a hook. Never touch: packets/, client/,
research/, other uncommitted files (commit only with `-- <paths>`).
Libraries: the standard library and the existing hook helpers.
Done: signed commits; tests (including the 200k-path case for 1); `bash tools/check.sh --since <base>`;
the receipt printed by the fixed `receipt.py --print` itself.
Stop: budget 60 min of work time; stop if a guard change would block the coordinator's own workflow
in a way tests cannot cover.
Base: d6843c0234.
