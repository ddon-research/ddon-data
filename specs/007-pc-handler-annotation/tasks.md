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
  T004b done (`research/T004b-extract-run.md`: PC 5,631 functions, `table_ok`; PS4 3,568; DWARF 3,568 / 34
  without CU; 131 of 1,040 PC callbacks not function starts in the database: 119 no function, 12 inside
  one, silently dropped). T004c: the extractor lists missing roots; `repair_functions.py` (dry run by
  default, checked, undo log). T004d: persistent work copy `ddon-data-007work`, repair, re-extract PC.
  T004c done (9587b311da: extractor v2 writes `missing_root` records, never expands the enclosing
  function; `repair_functions.py`, 95 tests). Decision: names left at a moved function's old start
  (e.g. `0x7C5C8D`) are not moved now; T007 names the function at its new start from its PC string and
  removes the stale label there, recorded in the undo log.
  T004d run (`research/T004d-repair.md`): dry run 909 ok / 119 to repair / 12 refused; apply 116 repaired,
  3 failed (script defect: undefining the old start deletes the function), re-extract 15 missing roots,
  orphan refs 38 -> 9. The writes were lost: the worker could not be closed (save/close denied), was
  killed, and the next headless open restored the packed base (coordinator check: 0/116). Decision
  (coordinator, 2026-11-03): database writes run only as headless `idat -A -S<script>` batch jobs ending in
  `qexit(0)` (checked: saves and packs); ida-mcp only reads. T004e fixes the script, T004f reruns.
- [ ] T005 Matcher with gates and tests, the precision check on withheld seeds, the manifest (`implementer`).
- [ ] T006 Types and locals rules over the accepted pairs (`implementer`, evidence from T004 dumps).
- [ ] T007 Apply script and the applied copy (`implementer` writes it, `evidence-researcher-ida` runs it).
- [ ] T008 Verify: re-extract, compare, decompile sample; adversarial review of pairs and types.
- [ ] T009 Close: `check.sh --all`, docs, retrospective, publish the database folder.

Order: T003 first (T002 needs a copy of the accepted database), then T002.

## Running

- T004e (implementer, brief `briefs/T004e-repair-fixes.md`), started 2026-11-03.
- Decision (coordinator, 2026-11-03): from T004d on, all writes go to one persistent work copy
  `PC_DDON_03040008/ddon-data-007work/` of the accepted database (repairs first, then T007's apply);
  it is published as `spec007-packet-handlers-<date>/` at the close.
