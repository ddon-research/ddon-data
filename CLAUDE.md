# Claude Code notes for ddon-data

@AGENTS.md

## Resume

- Root Spec Kit project: no features yet (`specs/` is created by `/speckit-specify`).
- Knowledge graph: `research/knowledge-graph/specs/001-pre-extraction-knowledge-graph/` is active;
  `research/knowledge-graph/specs/STATUS.md` is the dashboard.
- Flag investigation: `research/03040008/flags/TODO.md` and `plan/*.md`.

## Tools

- Spec Kit skills: `/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`,
  `/speckit-plan`, `/speckit-checklist`, `/speckit-tasks`, `/speckit-analyze`,
  `/speckit-implement`, `/speckit-converge`, `/speckit-taskstoissues` (installed in
  `.claude/skills/`, shared by both Spec Kit projects). For knowledge-graph features, run the
  scripts the skills call with `SPECIFY_INIT_DIR=research/knowledge-graph`.
- IDA: the `ida` (ida-mcp) and `ida-assist` MCP servers attach to the IDA 9.5 GUI databases listed
  in `AGENTS.md`; the user-level `CLAUDE.md` documents attach steps, database hashes, and the
  headless `ida-domain-scripting` skill. Prefer MCP over the headless skill for those databases.
- Use subagents for sweeps over `client/` or `packets/`, and keep only their conclusions.

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
