# 009 tasks

Coordinator: main session. One subagent at a time. Target structure and rules: `spec.md`.

- [x] T001 Census (`research/T001-census.md`, `T001-sections.tsv`, `T001-files.tsv`): 28 living docs, 6,228 lines, 285
  heading rows; 58 pages proposed; 121 file rows (27 move); tutorial proven on committed input (14.3.2); four more
  outside readers; 31 of the packet table's 587 fit counts stale.
- [ ] T002 Skeleton, writing contract, gate, tutorial, safe moves (`implementer`, `briefs/T002-foundation.md`).
- [ ] T003 Move the packet work to `packets/` (`implementer`, `briefs/T003-packet-tree.md`): patterns to
  `packets/patterns/03040008/`, `tools/`, `tests/`, `plbatch/`, `wireshark/`; guard narrowed to the data trees.
- [ ] T004 Packet and evidence pages: packets README split, Arrowgene/annotate adoc, wire format, handler tables, marks,
  decoding method, write-a-pattern, evidence model; `packet-ids.md` check; 31 counts corrected.
- [ ] T005 IDA and transfer pages: `ida-transfer/README.md` split, query and write how-tos, transfer method.
- [ ] T006 The rest: protections, patches, ELF dumps, plbatch, Pharos, textures, rng-race, `research/README.adoc`,
  `rLandInfo-example`, wikis; repository layout, inputs, tools, conventions, gate and hooks; root `readme.adoc`.
- [ ] T007 Review: accuracy sample, a reader's walk, adversarial check of the new gate.
- [ ] T008 Editor pass, `AGENTS.md` / `CLAUDE.md` shortened, close: `check.sh --all`, retro, merge and push.

## Decisions (coordinator, 2026-11-04, from T001 § 12)

1. Packet table: one Markdown reference file `docs/reference/packet-ids.md` with a check in the gate, edited by script.
2. `protections/README.md` and `elf-dumps/README.adoc` keep their paths and the sections outside readers cite (§1, §5;
   § 3, § 7): no outside repository needs an edit, so none is made. Also unmoved: `research/rng-race/`, `packets/keys/`,
   `research/claude-vision-tokens.md`, `binaries/PS4_02020005/elf-dumps/`.
3. `research/<build>/r*-pattern.cpp` stay flat; the 5 notes move out.
4. Moves: census § 8 steps 1-7 and 9. No `packets/statistics/`; `research/PS4`, `bbm`, `wireshark` stay.
5. Page count: the census's 58 is the map; thin pages merge (`run-flag-investigation` and `external-references`
   become index links).
6. Sam, 2026-11-04: packet work moves from `research/` to top-level `packets/`, including plbatch and the Wireshark
   dissectors (overrides decision 4 for `research/wireshark`). Checked: 0 dirty files in those trees, no sibling repository
   and no JSON names their paths. The build stays in the pattern path (`packets/patterns/03040008/`). `research/rng-race/`
   stays: ddon-hook's `tools/rng/` reads it by path.

## Running

- T002 (implementer, brief `briefs/T002-foundation.md`), started 2026-11-04. Next: land, apply its `AGENTS.md` lines,
  spawn T003 (brief written), then brief T004.
