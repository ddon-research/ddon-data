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
- [x] T004 Extract scripts for both databases (`implementer`), then the dumps (`evidence-researcher-ida`).
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
  T004e done (4cd15c65e3: del_func + add_func instead of moving the start; the three refusals accepted under
  checked conditions; batch entries, extract discards its session; 124 tests).
  T004f done (`research/T004f-repair-batch.md`: fresh work copy, batch apply 130 repaired / 1 refused
  (0x7D1BE0, switch in undefined code) / 0 failed; work copy sha `7189b4c6...`; re-extract `table_ok`,
  1 missing root; 9 spot checks decompile). Open for T007: 3 `OnPacket_*` labels left at old starts
  (0x7C5C8D, 0x7D714C, 0x7D858F). Note: a batch dry run also re-saves the copy (+242 B), nothing changed.
- [x] T005 Matcher with gates and tests, the precision check on withheld seeds, the manifest (`implementer`).
  Matcher done (499f7c701d: 150 tests; tier 0 669 of 1,040 callbacks named from PC strings, 364 without
  string, 6 shared, 1 no function; 467 seeds, all gate (c); propagation 0 proposals (uneven gaps, typically
  2 PC vs 4 PS4 calls); precision 5 x 93 withheld, 0 recovered, 0 wrong; 006 matched 146 agree / 209 not
  paired / 0 disagree; one wrong seed found and fixed: seeds must match the connection class). Next:
  role anchors (reader, codec width, sender by packet id): T005b evidence, then T005c.
  T005b done (`research/T005b-role-anchors.md`: 463/467 PC handlers call one reader; PS4 88 out-of-line
  `ReadPacket`, 378 inlined; 220/222 element-reader calls align in equal-width pairs = 117 1:1 pairs; 658
  PC `WritePacket` calls with constant g/id/sub, 408 RES seeds with one sender; REQ/RES by shared listener
  slot (327 PC / 321 PS4), names by convention only = I; five anchor rules proposed). Plan: T005c tools
  (call-site constant args, codec shape, externs; repair of undefined call targets), T005d batch run
  (repair + both re-extracts), T005e matcher anchors 1, 2, 4 (+3 as call-site naming, 5 later).
  T005c done (581571a37e: v3 call-site constant args (only with a known argument size), codec width by
  shape (1/2/4/8), extern records; repair roots include direct call targets, depth 3; 221 tests; not run
  on a database).
  T005d done (`research/T005d-batch-v3.md`: 125 call-target roots, 118 repaired / 7 refused / 0 failed, 55 in
  `0x758000`-`0x77C000`, none in the login range (no roots reach it); work copy sha `65120b34...8b9111`; PC
  v3 6,261 functions, 4,837 call sites with constants, 20 codecs all as T005b; PS4 3,568, codec shape
  classifier finds 4 of 22, so PS4 widths come from the codec symbols in T005e).
  T005e done (fd44c3fc37: 245 tests; rule 1 reader 69 accepted of 88, rule 2 element reader 56 of 104, rule 3
  694 codec call sites, rule 4 listener slot 0 (dumps lack slots and requesters); precision 5 runs, 0 wrong;
  negative control first accepted 2 wrong element pairs, gate added (no other fitting reader pairs either
  function differently), then 0 accepted in 5 runs; cross-checks no disagreement). Pairs now 467 + 125 = 592.
  Plan: T005f extractor v4 (object-relative accesses for the layout check, slot facts, requester roots,
  reader depth 8), T005g batch extract, then the matcher rerun with rule 4 and T006 types.
  T005f done (778d9264db: object-relative accesses with block-consistent register tracking, PS4 slot stores via
  `mpManager`, requester roots (PC `sNetworkExt::reserveNetworkErrorDialog` `0xBB39D0`, 581 sites; PS4
  `0x7EDF80`, 478), `codec_distance` depth 8; PC `callOnPacketFunc` slot already in v3 `const_stack`; 284 tests).
  T005g done (`research/T005g-extract-v4.md`: PC v4 7,262 functions, 48,235 access records, 581 requester
  sites, work copy unchanged; PS4 v4 4,146 functions but only 722 access records, 0 slot stores: the
  operand parser reads text and PS4 names argument registers; DWARF re-run 4,106 of 4,146).
  T005h done (a5131eff53, 7f31b5e868: extractor v5 decodes operands from `op_t` (SIB helpers from the IDA SDK
  `intel.hpp`); PS4 30,587 access records, 2,685 `mpManager` slot stores; rule 4: 107 requester + 234 sender
  pairs; element readers 56 -> 95 (deeper dumps), readers 69, call sites 926; fold key includes call-site
  immediates; control accepted 1 listener pair in 2 runs, slot-order check tightened, then 0; precision 0
  wrong in 5 runs; 297 tests). Accepted pairs: 467 + 69 + 95 + 107 + 234 = 972. IDA SDK clone line appended
  (uncommitted) to `research/external-references.jsonl`, which holds others' edits.
- [x] T006 (done 95bd50d7b4, wave 1: names 1,082 rows (1,077 set, 2 corrected, 3 stale labels; 88 already, 7
  conflicts); prototypes 1,011 (54 conflicts with earlier hand prototypes, 109 skipped: register argument
  other than ecx); types 106 structs accepted by the access check (84 `MtTypedArray<CDataX>` copies of one
  20-byte layout, 14 distinct non-template), 72 refused (most packet classes and `cNetGameServer`: PC
  accesses contradict the PS4 layout; `cSeedGameSvConnection`: bitfield in base `MtMemoryStream`), 183
  unchecked; comments 1,119; holdout: 48 types depend on a single seed, none new; 323 tests). Locals:
  wave 2. Conflicts settle in T007c. Types and locals rules over the accepted pairs (`implementer`, evidence from T004 dumps).
- [x] T007 Apply script and the applied copy (script done f913a776ad: tinfo/udt types, fail-closed on stale
  before-state, undo log, verify mode; 354 tests; IDA adapter not yet run). T007b dry run stopped by its
  10% gate (`research/T007b-apply-run.md`): 105/189 types refused because `MtObject`, `CPacketDataBase`,
  `MtArray` exist with equal layout but IDA's member names (`__vftable`, `baseclass_0`); work copy
  unchanged, rollback copy `.before-T007b.i64` made. T007c: equality and emission in IDA's conventions.
  T007c done (c91df1e373: `same_layout` treats vptr/base-class naming variants as equal by flags or names, base
  type names checked; `transfer/` already emitted IDA's forms; 360 tests). T007b rerun next.
  T007b rerun: dry run 0 refusals; apply wrote every row, 171 prototype read-backs `failed` on text
  compare (`struct ` prefix on `::`/template types); writes checked right on 4; rollback restored
  (`65120b34...`). T007d: compare prototypes as `tinfo_t`.
  T007d done (5362d5c45c, 9ab79f9303: `same_prototype` via `tinfo_t.compare_with(TCMP_EQUAL)` per part plus
  argument names, in already/read-back/verify; 366 tests). T007b run 3 next.
  T007b run 3 done (`research/T007b-apply-run.md` § Run 3: 182 types + 7 already, 1,079 names, 3 labels,
  1,011 prototypes, 1,119 comments, 0 failed; second apply all `already`; verify ok, 1,011/1,011 decompile;
  re-extract changes = written rows both ways; work copy `f17d0745...7829`). **False positive found** in the
  spot checks: `nUserSession::CPacket_S2C_CHANGE_JOB_RES` layout contradicted by the PC reader `0x80cf80`
  (access check accepted accesses inside members). Decision (coordinator): fix the check (T006b), regenerate,
  roll the work copy back to `.before-T007b.i64` and re-apply (T007e); then a reviewer re-derives a sample of
  accepted types from disassembly.
  T006b done (e49ae1b341: cause: a `lea` (no width) was accepted on any leaf start at any depth, 10 lea records of
  `0x80cf80` fell on inner fields; second hole: `MtObject**` stores counted as vptr writes; fixed: lea only on the
  object, its own members or array element starts; indexed scale = element size; 374 tests; accepted 98 -> 96:
  CHANGE_JOB_RES refused, MtObject and 7 sub-types unchecked). Remaining 96 = 90 `MtTypedArray<X>` (13/20 bytes
  width-checked) + 6 `CData*` on lea records only (0%). Decision: lea never accepts a type (T006c).
  T006c done (6dc8a6e496, 4254210930: the 6 lea-only types `unchecked`, opaque in `types.h`; accepted 90, all
  `MtTypedArray<X>`; prototypes/comments unchanged; typed-lea rule noted for wave 2; 376 tests).
  T007e stopped at its dry-run gate (`research/T007e-reapply.md`): rollback done (work copy `65120b34...`,
  run-3 kept as `.run3-T007b.i64`); 91/181 types refused, all from `MtArray`: its base is now an untransferred
  4-byte blob vs the database's `MtObject` base. T007f: equal when the class name and size match.
  T007f done (a56731c675: untransferred base compared by its class from the `base X (not transferred)` comment,
  database base kept; 381 tests). T007e resumes at step 2.
  T007e run 2 done (`research/T007e-reapply.md` § 6): 0 refusals, 0 failed; 177 types, 3 labels, 1,079 names,
  1,011 prototypes, 1,119 comments written; 7 name / 54 prototype conflicts reported only; second apply all
  `already`; verify ok, counts 788->965 local types, 51,074->52,148 names, 453->1,464 typed functions; 1,011/1,011
  decompile; re-extract changes = rows both ways; CHANGE_JOB_RES + 6 lea-only types forward-only. Work copy
  `be0cc624...162f`; rollback `.before-T007b.i64` kept. (`implementer` writes it, `evidence-researcher-ida` runs it).
- [x] T008 Verify: re-extract, compare, decompile sample; adversarial review of pairs and types.
  Adversarial review done (`research/T008-adversarial.md`, seed 8008: 70 sampled items over 9 strata, 0 wrong on
  PC; 2 tooling defects reproduced by the coordinator: F1 pointer depth dropped (`MtObject**` -> `MtObject *` in
  `types.h`), F2 member type not compared in `member_equal`; work copy right because its `MtArray` was kept).
  T006d fixes both; then a verify run on the work copy.
  T006d done (733a4c77e6: one pointer level stripped at a time; `member_equal` compares member types (`norm_type`
  maps scalar spellings); canaries are tests; manifest change `MtArray.mpArray` only; 405 tests). Verify of the
  work copy runs as T009 step 0.
- [x] T009 Conflicts with the earlier annotations. Evidence done (`research/T009-conflicts.md`,
  `T009-decisions.tsv`: 61/61 `ours`; 5 earlier names copy the group prefix into a PS4-style name, 2 earlier
  `__fastcall` contradicted by ecx use and `retn 8`; step 0 dry run all `already`, verify refused: manifest hash
  changed after T006d, fixed by the next apply log). T009b: correction rows + apply support; then T009c apply.
  T009b done (9e495f2362, 91bf570b8d: 7 names `correct`, 54 prototypes `replace` with the current-value guard;
  55 comment rows added (1,174; 13 `append` below existing comments, apply keeps only our part); 417 tests).
  T009c done (`research/T009c-apply.md`: 7 names, 54 prototypes, 55 comments written, 0 refused/failed; second
  apply all `already`; verify (new base `apply-t009c.jsonl`) all ok, 1,065 typed functions decompile; 13 earlier
  comments kept above the separator; `0x7DA410` keeps its `__userpurge` prototype (refused in skipped.tsv)). Work
  copy `f7f3a219...3c25`; rollback `.before-T009c.i64`. Snapshot published (coordinator):
  `PC_DDON_03040008/spec007-packet-handlers-20261103-wave1/2022_01_29_DDO_DUMP_FIX.exe.i64` (same sha256).
- [x] T010 Local variable names (evidence `research/T010-locals.md`, `T010-locals-walk.tsv`): PS4 DWARF locals bind
  to PS4 Hex-Rays variables (1,257 of 2,256 uniquely), but the spec's operation rule names 0 PC locals over 898
  pairs and the codec-anchor extension 3 (`nRet`), 0 conflicts: 3,235 of 3,321 PS4 defining calls go to
  unpaired callees; relaxing the size/array gates would name split packet pieces `packet` (wrong). Decision
  (coordinator): not implemented in wave 1 (single-digit yield); the levers are a wave-2 scope choice for Sam
  (PC layouts for packet classes; pairing context getters such as `sContextManager::getContextMyPlayer`).
- [x] T011 Close (2026-11-03), below.

## Close (2026-11-03): wave 1

- Gate `bash tools/check.sh --all` at eb1cdda52a (+ uncommitted CLAUDE.md learning): hooks, shell, flags, export,
  idacopy, xfer (417 tests), mcp passed; imhex not run (not on PATH); kg failed on `test_production_size_budgets`
  in the untracked, other-owned `research/knowledge-graph/` (as at the 006 close; no 007 commit touches it).
- Result on the work copy (`ddon-data-007work`, sha256 `f7f3a219...3c25`, published unchanged as
  `PC_DDON_03040008/spec007-packet-handlers-20261103-wave1/2022_01_29_DDO_DUMP_FIX.exe.i64`): 248 function starts
  repaired (130 handler callbacks, 118 call targets); 972 accepted pairs (467 handler seeds, 69 readers, 95 element
  readers, 107 requesters, 234 senders); 1,086 names (1,077 new + 9 corrections incl. 7 settled conflicts), 1,065
  prototypes with DWARF argument names, 177 types (90 access-checked `MtTypedArray<X>`, the rest forward
  declarations), 1,174 provenance comments; every row verified, every typed function decompiles. Precision: 0
  wrong pairs in 5 holdout runs, 0 accepted in 5 shuffled controls; T008 adversarial sample 70 items, 0 wrong.
  `ddon-hook`'s `CURRENT-RECOVERY.json` still points to its feature008 database (not changed: that pointer is
  ddon-hook's).
- False positives caught by the method and fixed: a game handler paired with the login handler of the same name
  (T005: class gate); 2 wrong element pairs in the first negative control (T005e gate); 1 listener pair in the
  control (T005h slot-order gate); `CHANGE_JOB_RES` layout accepted through `lea` coincidences (T006b/c: lea never
  accepts); `MtObject**` rendered as `MtObject *` and member types not compared (T008 F1/F2, T006d).
- Retro: the write path cost five apply rounds (T007b x3, T007e x2) on issues a real-IDA smoke test of the adapter
  would have caught at once (member naming conventions, printed-type comparison, opaque bases); next time run a
  tiny apply on a scratch copy right after the script lands. The extractor is one 1,680-line file whose edits
  returned ~19k tokens each to the implementer (retro top results); split it into modules before more work.
  ida-mcp workers cannot be closed in this repo, so all writes moved to headless batch (learning added to
  `CLAUDE.md`). Stale `.agent-ledger/running/` records after `waiting:` stops blocked every spawn (002 T022 open).
- Open for a wave 2 (Sam's choice): partial PC layouts for packet classes (refused today because Season 3 changed
  them), which would also unlock the `packet` locals; pairing context getters; typed-`lea` type acceptance; rule 5
  (packet object vtables); the login handler table (`0x888000`-`0x88E000`, not reached); 109 prototypes skipped for
  non-ecx register arguments; 0x7D1BE0 (switch in undefined code) unrepaired.

Order: T003 first (T002 needs a copy of the accepted database), then T002.

## Wave 2 (started 2026-11-03, Sam: "Why did you not just start it?")

Goal: the rest of Sam's request: packet-class types and local names, by operation, no false positives.

- [ ] T012 Evidence: codec destinations -> packet member links; anchored gap pairs (`briefs/W2-T012-evidence.md`).
- [ ] T013 Partial packet layouts from member links (implementer), then apply.
- [ ] T014 Wider pairs from anchored gaps (getters), then locals rules R1/R2 (implementer), then apply.
- [ ] T015 Review, close wave 2, merge and push.

## Running

- T012 (evidence-researcher-ida), started 2026-11-03.
- Decision (coordinator, 2026-11-03): from T004d on, all writes go to one persistent work copy
  `PC_DDON_03040008/ddon-data-007work/` of the accepted database (repairs first, then T007's apply);
  it is published as `spec007-packet-handlers-<date>/` at the close.
