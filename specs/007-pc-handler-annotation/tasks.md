# 007 tasks

Coordinator: main session. One subagent at a time. Method and rules: `spec.md`.

- [x] T001 Survey the earlier work (done: `research/T001-prior-method.md`; 50/1,040 handlers + 1 sender
  annotated from PC `OnPacket_` strings, PS4 links by name only; 24 overlaps with 006 T001 all agree;
  only the table reader and catalog reusable). Coordinator count: 675 PC `OnPacket_` strings, 460
  unique PS4 suffix matches.
- [x] T002 (done: `research/T002-audit.md`, `T002-prior-annotations.tsv` 2,981 rows; accepted copy sha matches, 107 views present; 50 earlier handler names hold (40 PS4 links proved by read widths, 10 unproved Season 3 diffs), sender `0x833670` name unproved, 1 wrong name `0x7D36B0`, 10 names without source; codec pairs settled by 298 aligned handler pairs; table 1,041/1,040 with 74 initializers to `0x1A36540`; tier 0: 580 callbacks with one `OnPacket_` string, 412 with a unique PS4 partner; PS4 IDA lacks DWARF locals) Audit the earlier packet annotations in the accepted PC database (`evidence-researcher-ida`):
  inventory (names/types/comments in the packet area), a sampled independent check against PS4, and
  the readiness of the PS4 database (DWARF prototypes, locals, types present).
- [x] T003 (done 5801c721a1: `private-copy.sh pc-accepted <name>`, sha-checked against the record; test `research/ida/tests/private-copy.sh`, 14 checks, check.sh section idacopy) Private copy of the accepted PC database (`implementer`): `research/ida/private-copy.sh` target
  for the accepted database, read from `CURRENT-RECOVERY.json`; the IDA guard still allows only copies.
- [ ] T004 Extract scripts for both databases (`implementer`), then the dumps (`evidence-researcher-ida`).
  Scripts done (15322cb3d0: `research/03040008/ida-transfer/` uv project, `extract_ida.py` + `extract_dwarf.py`
  (pyelftools + capstone; reconstructor output covers only resource code), 59 tests; PS4 DWARF dump 3,540
  functions / 7,609 params / 6,632 locals / 8,652 types in 341 s, 34 scope functions in no CU). T004b runs them.
- [ ] T005 Matcher with gates and tests, the precision check on withheld seeds, the manifest (`implementer`).
- [ ] T006 Types and locals rules over the accepted pairs (`implementer`, evidence from T004 dumps).
- [ ] T007 Apply script and the applied copy (`implementer` writes it, `evidence-researcher-ida` runs it).
- [ ] T008 Verify: re-extract, compare, decompile sample; adversarial review of pairs and types.
- [ ] T009 Close: `check.sh --all`, docs, retrospective, publish the database folder.

Order: T003 first (T002 needs a copy of the accepted database), then T002.

## Running

- T004b (evidence-researcher-ida, brief `briefs/T004b-run-extractors.md`), started 2026-11-03.
