009 T006: IDA and transfer pages

Objective: a peer can query and annotate the IDA databases safely and can re-run or understand the PS4 -> PC annotation transfer without reading spec 007. PC 03040008, PS4 02020005. Read `specs/009-docs-structure/spec.md`, `docs/reference/documentation-style.md` (binds every page), the `research/03040008/ida-transfer/README.md` rows of `specs/009-docs-structure/research/T001-sections.tsv`, and `T001-census.md` §2-§3. Move text by script where it moves whole; polish is the editor's, later.

**Pages**
- `docs/how-to/query-ida-read-only.md`: private copy (`pc`, `pc-accepted`, `ps4`, the new target below), which server and worker, the `guard_ida` rule, opening and querying, deleting the copy. From `CLAUDE.md` Tools, `research/ida/private-copy.sh`, the README's Read path, the `ida-tooling` skill's facts a peer needs.
- `docs/how-to/write-to-an-ida-database.md`: headless batch `idat -A -L<log> -S"<script>" <copy>.i64`, script ending in `qexit(0)`, read-only scripts setting `DBFL_KILL`, why a killed worker's writes are lost, checking the save, keeping the before-state and the undo. Never the user's database.
- `docs/how-to/transfer-annotations-ps4-to-pc.md`: extract, repair, match, transfer, apply, verify, undo: the commands, order, what success looks like. Check each command against the script's `--help` or argument parser; say which you ran. Do not run an apply.
- `docs/reference/ida-transfer-tools.md`: the scripts and their flags, the extractor's schema and versions (the README's "Version 3/4/5/6" sections become one description of what the extractor emits, not a history), the manifest's columns, the matching and transfer rule lists, published results' locations.
- `docs/explanation/ida-transfer-method.md`: why pairs are proven by code shape and not names; the matcher's gates and what each false positive taught, as the failure it prevents, with no task ids; the holdout and shuffled-partner controls; why a `lea` never accepts a type; what the method leaves out and what the results mean for a reader of the database. Stability test applies: counts go to `docs/reference/status.md`.
- `research/03040008/ida-transfer/README.md` becomes short: what the directory holds, who produces it, links.
- Add the annotated database to `docs/reference/status.md` if a count belongs there. `docs/reference/packet-handler-tables.md` drops its "no target" note.

**A small tool gap the docs exposed**: `research/ida/private-copy.sh` has no target for `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64`, the annotated database. Add target `pc-handlers` beside the others (same hashing and copy rules, copy under `PC_DDON_03040008/ddon-data-<name>/`, no write to the original), its case in `research/ida/tests/private-copy.sh`, and check `tools/hooks/guard_ida.py` allows the copy and still refuses the original. Update the usage comment. Prove with a real copy of a small test fixture path per the test's convention, not a full database copy unless the test requires it.

**No fact lost**: `specs/009-docs-structure/research/T006-moves.md`: a table saying where each README section went or why it was cut; a script spot-check over hex addresses, flag names and script names in the old README against the pages and the cut list, misses fixed.

Update `docs/index.md`, the glossary. List `AGENTS.md` / `CLAUDE.md` lines for the coordinator (`private-copy.sh <pc|ps4>` is incomplete there; the IDA learning can point to the how-to).

Owns: `docs/**`, `research/03040008/ida-transfer/README.md`, `research/ida/private-copy.sh`, `research/ida/tests/private-copy.sh`, `specs/009-docs-structure/research/T006-*`.
Never touch (other work, dirty): `research/03040008/flags/**`, `research/knowledge-graph/`, `binaries/PS4_02020005/DDOORBIS.elf.h`, `packets/decrypt-annotate-streams.sh`, `research/external-references.jsonl`, `research/external/*`, `patches/2026_10_17_*`, `specs/*-1.md`, `client/`, packet data, the original or published IDA databases.
Source boundary: `specs/007-pc-handler-annotation/spec.md`, `tasks.md` Close sections and reports by section (`rg` first). The role-file rule stands: never open the user's `.i64`.
Libraries: stdlib; existing tools.
Done: `bash tools/check.sh --since <base>` with `docs`, `xfer`, `idacopy`, `hooks` passed; signed commits with `git commit -m <msg> -- <paths>`; receipt with "For Sam's inspection" (pages added, commands run and not run, facts you doubted, `AGENTS.md`/`CLAUDE.md` lines).
Stop: budget 90 min of work time; past 300k context, commit what passes and end `cut short:` with what is left. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
