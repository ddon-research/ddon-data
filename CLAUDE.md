# Claude Code notes for ddon-data

@AGENTS.md

## Resume

- Root Spec Kit project: no feature is active. `specs/010-server-packet-fixes/` is closed, its output draft
  [PR 8](https://github.com/Sehkah/Arrowgene.DragonsDogmaOnline/pull/8) on the fork; upstream on hold by Sam
  (`specs/010-server-packet-fixes/tasks.md`, T007f). `specs/001-ps4-static-dumps/` (PS4 ELF
  static dumps) is closed; its output is `binaries/PS4_02020005/elf-dumps/`, with the comparison material in
  the gitignored `elf-dumps/archive/`.
- Knowledge graph: `research/knowledge-graph/specs/001-pre-extraction-knowledge-graph/` is active;
  `research/knowledge-graph/specs/STATUS.md` is the dashboard.
- Flag investigation: `research/03040008/flags/TODO.md`.
- PC client protections, patch lineage and crash triage: `docs/explanation/client-lineage-and-protections.md`, `docs/how-to/triage-a-client-crash.md`; `research/03040008/protections/README.md` keeps the cited section numbers
  (spec `specs/003-client-protections/`, done); outside references: `research/external-references.md`.

## Tools

- Spec Kit skills: `/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`,
  `/speckit-plan`, `/speckit-checklist`, `/speckit-tasks`, `/speckit-analyze`,
  `/speckit-implement`, `/speckit-converge`, `/speckit-taskstoissues` (installed in
  `.claude/skills/`, shared by both Spec Kit projects). For knowledge-graph features, run the
  scripts the skills call with `SPECIFY_INIT_DIR=research/knowledge-graph`.
- IDA: the `ida` server (headless ida-mcp, registered at local scope with
  `claude mcp add -s local ida -- uv run --no-dev --project <ida-mcp plugin cache dir> ida-mcp stdio --agent=claude`)
  and the role `evidence-researcher-ida`, which starts its own copy of it. The worker saves what
  it opens, so open only a private copy: `bash research/ida/private-copy.sh <pc|pc-accepted|pc-handlers|ps4> <name>`
  prints its path (beside the original, in `ddon-data-<name>/`); the hook `guard_ida` refuses any
  other path and `save_database` is denied. Query read-only. Prefer MCP over the raw
  `binaries/PS4_02020005/*.elf.c` exports and over the `ida-domain-scripting` skill.
- Delegation: load the `coordinate` skill and use the role agents (`AGENTS.md` "Agents and
  coordination"); sweeps over `client/` or `packets/` go to a `repository-researcher`, and only
  its conclusions stay here.

## Bash tool traps

- The Bash tool `eval`s each command, stripping one level of escaping. Put text with backslashes
  or quotes in a file written with the Write tool, or use `rg -F` / `sd -F`.
- `fd` and the Glob tool behave differently: `fd` honours `.gitignore` (so it hides `.claude/`),
  Glob does not. Pass `-H -I` to `fd` when looking for ignored files.
- `python` on `PATH` may resolve to the legacy root `.venv` when `VIRTUAL_ENV` is set; use
  `uv run` inside a project instead.

## Learnings

Keep at most 15 entries. Replace stale entries; do not append history.

- `specify init --here --force` preserves an existing `.specify/memory/constitution.md`,
  `feature.json`, and `AGENTS.md`; it adds scripts, templates, and skills only.
- IDA database writes run only as headless batch jobs (`idat -A -L<log> -S"<script>" <copy>.i64`, the
  script ending in `qexit(0)`; read-only scripts set `DBFL_KILL` first). ida-mcp workers cannot be closed
  here (`save_database`/`close_database` denied); a killed worker's writes are lost, because the next
  open restores the packed base (007 T004d). Recipes: `docs/how-to/write-to-an-ida-database.md`.
- A push to a public repository publishes commit messages, code comments and test bodies, as well as the PR body: write
  them to the same standard from the first commit, and read `git log -p` before pushing (010 T006, T006a).
- A check on a client-supplied value is backed by a captured value, never by the value a test assumes; a ruling table
  lists every candidate, since a verdict on one part of a row can hide the rest (010 T005 F1, T007b finding 3).
