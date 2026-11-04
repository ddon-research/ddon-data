009 T001: census of the documentation and of the loose files

Objective: everything the next packages need to restructure the documentation by Diataxis (tutorial, how-to, reference,
explanation) and to move loose files, without losing a fact or breaking a reader. Read `specs/009-docs-structure/spec.md`
(target structure, rules). The contract being adapted: `C:/ddon-dwarf-reconstructor-rust/docs/reference/documentation-style.md`;
its how-to `docs/how-to/write-documentation.md` and `.claude/agents/editor.md` show the practice; ddon-hook's
`docs/development/08-documentation-style.md` is a second example. Read-only everywhere but your report.

Deliver `specs/009-docs-structure/research/T001-census.md` plus two TSVs next to it:

1. `T001-sections.tsv`: one row per section (heading) of every living doc: `readme.adoc`, `AGENTS.md`, `research/readme.adoc`,
   `research/03040008/packets/README.md`, `research/03040008/ida-transfer/README.md`,
   `research/03040008/protections/` (README, R1-R3), `patches/README.md`, `research/03040008/flags/README.md`,
   `binaries/PS4_02020005/elf-dumps/README.adoc`, `research/imhex/plbatch/README.md`, `research/pharos/README.md`,
   `research/rng-race/*.md`, `research/textures/*`, `research/rLandInfo-example.adoc`, `research/wikis-and-resources.adoc`,
   `research/claude-vision-tokens.md`, `research/external-references.md`, `research/03040008/quest-flag-data-source-mapping.adoc`,
   `packets/README-decrypt-annotate-streams.adoc`, plus any other doc you find outside `specs/`, `client/`, `packets/decrypted_*`.
   Columns: file, heading, lines, type (tutorial / how-to / reference / explanation / history / status), target page
   under `docs/` (or `keep` in a directory README, or `spec-history`: already recorded in a named spec, may be cut), notes.
2. `T001-files.tsv`: one row per loose file or small directory whose home is unclear: the top level of `research/`,
   the 60-odd `research/03040008/r*-pattern.cpp` and other loose files of `research/03040008/`, the top level of `packets/`
   (not its `decrypted_*`/`encrypted_streams` trees), `research/PS4`, `research/bbm`, `research/external`, `research/wireshark`,
   `tools/`. Columns: path, what it is, every reader found, git status (tracked / dirty / untracked), proposed path or
   `stay`, reason. Readers: search this repo's live files (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `tools/`, scripts, READMEs) and
   the sibling repositories `D:/ddon-explorer-server`, `D:/DDON-translation`, `C:/Users/morph/CLionProjects/ddon-hook`,
   `C:/ddon-dwarf-reconstructor-rust`, `D:/ddon-extractor`, `D:/ddon-ghidra-scripts`, `D:/ddon-data-s1`, `D:/ddon-data-s2`
   (their tracked files, with `rg`, bounded). Include relative paths inside scripts that would break if moved. Closed specs
   do not count as readers.
3. The report: the proposed page list per quadrant (title, one-line purpose, source sections), naming the gaps (workflows
   and facts with no page anywhere, knowledge only in `specs/00[5-8]*/tasks.md` or reports that belongs on a page: e.g. the
   packet wire format, marks V/I/G, handler table, the ida-transfer method, IDA batch-write recipes, the fit rule);
   a candidate tutorial on a fixed committed input that is guaranteed to work and needs no IDA or game client (say which
   input and which commands, and run them to prove it); stale facts with their evidence (known: `plan/` is named by `AGENTS.md`,
   `CLAUDE.md` and `readme.adoc` but absent at the top level; `research/README.adoc` is named but the file is `research/readme.adoc`);
   the proposed split of `research/03040008/packets/README.md` (1,215 lines; which parts become how-to, explanation, a mark
   legend; its per-id table as a reference file, and whether part of it can be generated from the patterns' `// packet-id:` lines
   and marks); which paths must not move because of outside readers; proposed moves in order, largest benefit first; whether the
   per-season loose pattern layout (`research/<build>/r*-pattern.cpp`) should change given `research/02030004` must stay.

Scope limits: never list `client/` or `packets/decrypted_*` unbounded. Do not read files in `research/knowledge-graph/`
beyond naming it as other work (it has its own Spec Kit project); `research/03040008/flags/` is dirty other work: census its
README but propose no move.
Libraries: `rg`, `fd`, `git ls-files` with pathspecs, `jq`, stdlib Python.
Done: the report and two TSVs, every living doc section listed (say how you checked the row counts against the headings); your final
message: the path, the counts, the top 5 decisions you would ask the coordinator to make.
Stop: budget 60 min of work time. Base: d221d60a16.
