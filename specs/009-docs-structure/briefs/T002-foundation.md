009 T002: the docs skeleton, the writing contract, the gate, the tutorial, the safe moves

Objective: everything later page packages stand on. Read `specs/009-docs-structure/spec.md` and
`specs/009-docs-structure/research/T001-census.md` (§2 page list, §4 tutorial, §5 stale facts, §7 paths that must not move,
§8 moves; `T001-files.tsv` has per-file rows).

1. **`docs/reference/documentation-style.md`**: the writing contract, adapted from
   `C:/ddon-dwarf-reconstructor-rust/docs/reference/documentation-style.md` for this repository. Keep: the reader (peers
   who know x86, ELF, DWARF and Python, not this project's specs); level of detail by page type and the stability test;
   one purpose per page and the opening paragraph; facts come from the source; status words; keeps the lesson, drops the story;
   does not repeat agents' rules (`AGENTS.md` is canonical for agents); no word that dates a page; terms; diagrams (Mermaid,
   question-sentence first, about twelve nodes). Change: no site build, so Markdown links may point at repository files (the gate checks them);
   no arc42 subtree; every client fact names its build; evidence marks `V`/`I`/`G` keep their meaning on pages; counts live in
   `docs/reference/status.md` and dated reference examples. Directory README rule (spec). `research/03040008/flags/` and
   `research/knowledge-graph/` are other work: pages link to them, never restate them.
2. **`docs/index.md`**: the map, by type, listing only pages that exist. Pages to create now: `tutorials/read-one-packet.md`
   (census §4, verify every command and value yourself), `how-to/run-the-gate.md`, `how-to/write-documentation.md`,
   `reference/documentation-style.md`, `reference/glossary.md` (the census's terms so far, later packages add), `reference/status.md`
   (dated counts: packets decoded and fit totals as of 008's close, what was not run). Empty quadrant folders do not exist in git: no placeholder pages.
3. **The gate**: `tools/docs_check.py` plus a `docs` section in `tools/check.sh`, and tests in the style of `tools/hooks/test_*.py`. Fix `SMALL_TREES`
   (`plan` gone, `docs` added). Checks over `docs/**/*.md`, `readme.adoc` where feasible, and the short READMEs the spec names:
   (a) every relative link resolves to a file in `git ls-files`, compared **case-sensitively** (the census found a case mismatch a Windows
   filesystem check cannot see; `core.ignorecase=true`); new, untracked docs must count, so the set is index plus untracked `docs/`;
   (b) anchors resolve to a heading in the target; (c) every page is reachable from `docs/index.md` and listed once;
   (d) a repository path in a code span that starts with a known top directory (`client/`, `packets/`, `research/`, `binaries/`, `patches/`, `tools/`, `specs/`, `docs/`) exists,
   globs and `<placeholders>` skipped; (e) the writing contract's mechanical rules outside fences and code spans: task ids (`T\d{3}`, `R\d[a-z]?`-style package labels, wave names) and dating
   words the contract lists; (f) the opening: a paragraph comes right after the title; (g) the tutorial's inputs still match their three SHA-256 and its `jq` line.
   Each check has a failing fixture in the tests. The gate must not read `client/` or the JSON trees beyond the named files. Fast: under 10 s.
   Libraries: `markdown-it-py` (through `uv run --with`, or a small pyproject under `tools/`) for parsing rather than regex over Markdown; the rest stdlib; lychee and
   similar do not do (a) with git's case or (c)-(g), give that reason in the receipt. If `uv` cannot resolve it offline in the gate, the section prints `not run` with the reason, never `passed`.
4. **Safe moves** (census §8 steps 5, 6, 9), `git mv`, readers updated in the same commit, each directory with its short README:
   `research/scripts/` (the 7 scripts), `research/03040008/notes/` (5 notes), `research/prompts/` (3 `gpt-*`). Rename `research/readme.adoc` to its real on-disk case, `research/README.adoc`, by two `git mv` steps (content stays for a later package).
   Do not touch `AGENTS.md` / `CLAUDE.md`: list every line needing change in the receipt; the coordinator applies them. Not `packets/statistics/`, and `research/PS4`, `bbm`, `wireshark` stay.
   All `research/<build>/r*-pattern.cpp` stay flat.
5. **`.claude/agents/editor.md`**: a role for later specs, from `C:/ddon-dwarf-reconstructor-rust/.claude/agents/editor.md`, adapted to this repository (no worktree, `effort: medium`, `model: inherit`, path guard
   `guard_paths.py --allow 'docs/*' 'readme.adoc' ...` and the short READMEs; wording only, never a fact; reports facts it doubts). If your path guard refuses `.claude/`, leave the file at
   `specs/009-docs-structure/research/editor.md.proposed` and say so.

Owns: `docs/**`, `tools/docs_check.py`, its tests, `tools/check.sh`, the moved files and their readers named above, `research/scripts/`, `research/prompts/`, `research/03040008/notes/`, `.claude/agents/editor.md`, new READMEs of those directories, `specs/009-docs-structure/research/T002-*`.
Never touch (other work, dirty): `research/03040008/flags/**`, `research/knowledge-graph/`, `binaries/PS4_02020005/DDOORBIS.elf.h`, `packets/decrypt-annotate-streams.sh`, `research/external-references.jsonl`, `research/external/*`, `patches/2026_10_17_*`, `specs/*-1.md`, `client/`, packet data.
Libraries: as in item 3.
Done: `python` tests for the gate pass, each failing fixture proven to fail; `bash tools/check.sh --since <base>` with the `docs` line passed; the tutorial's commands re-run with their output compared, on the date stated; signed commits with `git commit -m <msg> -- <paths>` (stage directories explicitly, `git add -- <dir> <dir>`); receipt with "For Sam's inspection" (moved paths old -> new, `AGENTS.md`/`CLAUDE.md` lines to change).
Stop: budget 90 min of work time. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
