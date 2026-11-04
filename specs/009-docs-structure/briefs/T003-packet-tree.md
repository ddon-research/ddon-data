009 T003: move the packet work into the top-level `packets/`

Objective (Sam, 2026-11-04: "move the packet-related activity from research into the top-level packets folder as well incl.
imhex/plbatch"; "Same for the wireshark dissectors"): patterns, the export engine and the dissectors sit beside the data they
produce and read. Moves only: no pattern, include or JSON content changes beyond paths.

| Old | New |
| --- | --- |
| `research/03040008/packets/*-pattern.cpp`, `include/`, `README.md` | `packets/patterns/03040008/` (the build stays in the path: a pattern's layout is a claim about one client build) |
| `research/03040008/packets/tools/` | `packets/tools/` |
| `research/03040008/packets/tests/` | `packets/tests/` |
| `research/imhex/plbatch/` | `packets/plbatch/`; `research/imhex/` is then empty and goes |
| `research/wireshark/` | `packets/wireshark/` |

`packets/*.sh`, `packets/keys/` and the statistics files stay where they are. `packets/decrypt-annotate-streams.sh` is dirty other work: never edit
or stage it (the census found it names no moved path; verify). `research/rng-race/` stays (ddon-hook reads it).

1. `git mv` all of it. Physically move the gitignored `plbatch/build/` too (43 MiB, no rebuild); `.gitignore` follows. Check the executable still runs from there.
2. Update every live reader, found by `rg` for `research/03040008/packets`, `research/imhex`, `research/wireshark`, `wireshark-ddon` and for relative forms (`../research`, `$here/../../..`): `packets/imhex-export.sh` (defaults, usage text, messages),
   `packets/tests/imhex-export-select.sh`, `packets/tools/*.py` (including the `--patterns` default), `packets/plbatch/{build,test}.sh`, `tools/check.sh` (export section and its comments), `.gitignore`, the moved `README.md`, comments in patterns and includes that name a path, `docs/**`, the tutorial and its gate hash path in `tools/docs_check.py`, `research/README.adoc`, `research/03040008/ida-transfer/`, `readme.adoc`, `.claude/`. Closed specs stay as they are. Do not edit `AGENTS.md` / `CLAUDE.md`: list the lines for the coordinator.
   `research/knowledge-graph/` and `research/03040008/flags/` are other work; a search of their `src`/`tests` for these paths found nothing: re-check and report.
3. **Guards**: `tools/hooks/guard_bash.py` treats all of `packets/` as a large tree, so normal work on patterns would be refused. Exempt exactly the small subtrees (`packets/patterns`, `packets/tools`, `packets/tests`, `packets/plbatch`, `packets/wireshark`) from `LARGE_TREES` handling; a bare `packets/`, `packets/decrypted_*`, `packets/encrypted_streams` stay refused. Add cases to `tools/hooks/test_guard_bash.py` for both sides, including `./`-prefixed and absolute spellings and a `packets/patterns/../decrypted_json` traversal. `packets/plbatch/build/` holds a large source tree: note what `fd` over it does. `guard_paths.py` protects only the data trees (verify: an Edit of a file in `packets/patterns/` passes, one in `packets/decrypted_json/` is refused). `tools/check.sh` `SHELL`-section globs should cover the moved scripts.
4. **Prove nothing changed**: JSON byte-identical after re-exporting a stratified sample: 6 ids across at least 3 groups, one using several includes (`packets/imhex-export.sh --force @ <name> </dev/null`) with `git status --short -- packets/decrypted_json` empty afterwards, bounded by pathspec. plbatch `test.sh` passes from its new home. The `unk_correlate` tests, the export gate and the hook tests pass. Count: patterns before and after equal (595), `git log --follow` works on one pattern. `git diff -M --stat` shows only renames plus the named reader edits.

Owns: the moved trees, `packets/imhex-export.sh`, `tools/check.sh`, `tools/docs_check.py`, `tools/hooks/guard_bash.py`, `tools/hooks/test_guard_bash.py`, `.gitignore`, `docs/**`, `research/README.adoc`, `readme.adoc`, `specs/009-docs-structure/research/T003-*`.
Never touch (other work, dirty): `research/03040008/flags/**`, `research/knowledge-graph/`, `binaries/PS4_02020005/DDOORBIS.elf.h`, `packets/decrypt-annotate-streams.sh`, `research/external-references.jsonl`, `research/external/*`, `patches/2026_10_17_*`, `specs/*-1.md`, `client/`, packet data (the re-export sample must leave it unchanged).
Libraries: `git mv`, `sd -F`, `rg`.
Done: the checks of item 4 with counts; `bash tools/check.sh --since <base>`; signed commits with `git commit -m <msg> -- <paths>`, with the pure renames in one commit and the reader edits in the next so review stays readable if that works with the gates; receipt with "For Sam's inspection" (old -> new, the guard change and why, `AGENTS.md`/`CLAUDE.md` lines to change).
Stop: budget 60 min of work time. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
