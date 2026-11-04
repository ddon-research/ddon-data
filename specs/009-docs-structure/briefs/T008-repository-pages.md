009 T008: the repository-level pages and the root readme

Objective: a newcomer lands on `readme.adoc`, reaches `docs/index.md`, and finds where everything is, what goes in, and how the resource workflow runs. Read `specs/009-docs-structure/spec.md`, `docs/reference/documentation-style.md` (binds every page), `docs/index.md`, the relevant rows of `specs/009-docs-structure/research/T001-sections.tsv` and `T001-files.tsv`, `T001-census.md` §2, §5, §7. Move text by script where it moves whole; polish is the editor's, later.

**Pages**
- From `research/README.adoc`, `research/rLandInfo-example.adoc`, `research/scripts/`: `docs/how-to/decode-a-resource-format.md` (IDA first; Ghidra only as the archived alternative, per `AGENTS.md`), `docs/how-to/choose-a-resource-target.md`. The rLandInfo walk becomes the worked example in that how-to or its own section; delete the old files when their facts have landed. Coverage figures go to `docs/reference/status.md`, dated. Then `research/README.md` short (rename `research/README.adoc`; a Markdown short page matches the others; the `.adoc` has no outside reader per the census: recheck).
- `docs/how-to/extract-client-resources.md`: from `readme.adoc` and `AGENTS.md` Workflows; check against `D:/ddon-extractor/README.md`.
- `docs/reference/repository-layout.md`: every top path and each directory that matters under it, what it holds, who produces it, who reads it from outside (census §7, with file evidence), including `docs/`, `tools/`, `specs/`, and the Season 1 and 2 patterns now in `D:\ddon-data-s1`, `D:\ddon-data-s2` (`research/<build>/`). Data flow diagram from `readme.adoc`, updated: `packets/` holds its patterns and engine.
- `docs/reference/inputs-and-builds.md`: builds, game clients, IDA databases (and the `private-copy.sh` targets), PS4 ELF, captures, the longplay videos (the paragraph waiting in `research/rng-race/README.md` moves here).
- `docs/reference/tools-and-shell.md`: tools and versions a human needs: summary only, `AGENTS.md` is canonical for agents. `docs/reference/conventions.md`: naming and file formats. `docs/reference/gate-and-hooks.md`: each section of `tools/check.sh` and when it runs, what each hook in `tools/hooks/` refuses (from the code).
- `docs/reference/community-resources.md` from `research/wikis-and-resources.adoc` (external URLs not checked: say `not run`; delete the old file). `docs/reference/quest-flag-sources.md` from `research/03040008/notes/quest-flag-data-source-mapping.adoc` (keep it in notes as well only if the flag project's README cites it: check, read-only).
- `docs/reference/status.md`: re-read as a whole; one banner date per measured block; no duplicates.
- Index links only, no page: the flag investigation (`research/03040008/flags/README.md`), `research/knowledge-graph/`, `research/external-references.md`.

**`readme.adoc`** (root, keep the name): short. What the repository is; one small table of the top-level directories; the four doc types with a link each; the tutorial first; season repositories; credits; "provided for research, interoperability, and educational purposes". No workflows, no method. Fix the stale claim: DDOn-Tools does not read a path here (census §5), and no Season 1/2 pattern path remains. Keep the credits' content.

**Short READMEs still missing** (census §2): `research/03040008/dumps/`, `research/03040008/xfs/`, `tools/`. Add to `SHORT_READMES`.

**Gate coverage**: `tools/docs_check.py` has `SHORT_READMES` and an `adoc` default; confirm `readme.adoc` is checked. Add a check that no page or short README names a path under `research/01020003` or `research/02030004` as if local, unless it says which repository it means (use the existing code-span path check: such spans already fail unless excluded; report what it does).

**The index**: `docs/index.md` lists every page exactly once under its type, grouped so 70-odd pages stay scannable (for example how-to by packets, IDA, client, resources), each with a one-line purpose; the tutorial comes first; an "I want to ..." entry for the most common goals may lead it.

**No fact lost**: `specs/009-docs-structure/research/T008-moves.md`; a script spot-check of paths, commands and URLs in the deleted or shortened docs against pages and the cut list, misses fixed.

List `AGENTS.md` / `CLAUDE.md` lines for the coordinator (its Facts table may shrink to what an agent must know, with a link to the layout page: propose the text, line by line).

Owns: `docs/**`, `readme.adoc`, `research/README.adoc` -> `research/README.md`, `research/rLandInfo-example.adoc`, `research/wikis-and-resources.adoc`, `research/rng-race/README.md`, new READMEs named above, `tools/docs_check.py`, `tools/test_docs_check.py`, `specs/009-docs-structure/research/T008-*`.
Never touch (other work, dirty): `research/03040008/flags/**`, `research/knowledge-graph/`, `binaries/PS4_02020005/DDOORBIS.elf.h`, `packets/decrypt-annotate-streams.sh`, `research/external-references.jsonl`, `research/external/*`, `patches/2026_10_17_*`, `specs/*-1.md`, `client/`, packet data, sibling repositories (read only).
Libraries: stdlib; existing tools.
Done: `bash tools/check.sh --since <base>`, any section it skips that you changed code in run by hand; how-to commands checked against the scripts, saying which you ran (`research/scripts/find-unsupported-extensions.sh 03040008` is cheap; no re-extraction, no game client); signed commits with `git commit -m <msg> -- <paths>`; receipt with "For Sam's inspection" (pages added, files deleted, facts you doubted, `AGENTS.md`/`CLAUDE.md` lines).
Stop: budget 120 min of work time; past 300k context, commit what passes and end `cut short:` with what is left. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
