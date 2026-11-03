# 007 T007e: roll back and re-apply (PC 03040008): run 1 stopped at the dry run; run 2 passed (section 6)

Build PC 03040008, work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
(header `input_sha256` `f1c974d0...fa20`, `idb_path` under `ddon-data-007work`). Base `45979871475`,
2026-11-03 13:10-13:20 (WEST). IDA work by `C:/Program Files/IDA Professional 9.5/idat.exe` batch only;
ida-mcp was not used. Addresses are VAs (image base `0x400000`, 32-bit). `apply_transfer.py` sha256
`a8a84254...9c88` (unchanged since T007b run 3, `script_version` 1).

**Outcome: the rollback is done and verified. The dry run then refuses 91 of 181 type rows (50.3%), which is over
the 10% stop threshold of T007b's step 2, so the run stopped there.** One root refusal causes the whole cascade:
`MtArray` is `different-local-type`. T006b (`e49ae1b3416`) made `MtObject` opaque, so `types.h` now renders
`MtArray`'s base as `unsigned __int8 baseclass_0[4]`. The database's existing `MtArray` has an `MtObject` base, and
`apply_transfer.member_equal` requires the base's type name to equal the row's C type. Steps 3-7 and the extra
spot checks were **not run**. The work copy was not written: its sha256 still equals the rollback copy's. Because
the checks did not all pass, the run-3 database copy was **kept**.

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"

## 1. Rollback (verified)

    cd ddon-data-007work; sha256sum *.i64
    mv 2022_01_29_DDO_DUMP_FIX.exe.i64 2022_01_29_DDO_DUMP_FIX.exe.run3-T007b.i64
    cp -p 2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64 2022_01_29_DDO_DUMP_FIX.exe.i64
    sha256sum *.i64     # 13:11

| File | sha256 | bytes | mtime |
| --- | --- | ---: | --- |
| work copy before (run 3) | `f17d0745ac939e99f6389d85bb17ddc9eb97b7bc6a806eae2374aefbaf907829` | 112,375,929 | 12:50 |
| `...exe.run3-T007b.i64` (the `mv`) | `f17d0745...07829` | 112,375,929 | 12:50 |
| `...exe.before-T007b.i64` (rollback copy) | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 | 10:03 |
| work copy after the `cp` | `65120b34...8b9111` | 111,886,983 | 10:03 |

Run-3 dumps and logs were renamed to `*.run3.*`: `dumps/apply-dryrun.run3.jsonl`, `apply.run3.jsonl`,
`apply-2.run3.jsonl`, `apply-verify.run3.jsonl`, `pc-ida-applied.run3.jsonl`, and `dumps/logs/apply-dryrun.run3.log`,
`apply.run3.log`, `apply-2.run3.log`, `apply-verify.run3.log`, `pc-ida-applied.run3.log`,
`apply-spot-check.run3.log`, `apply-spot-check-b.run3.log`.

## 2. Dry run (stop condition)

    "$IDAT" -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # 13:11, rc 0, 12.5 s

- `dumps/apply-dryrun.jsonl`: sha256 `e462226a9fdb7d0833e1ccbb3c767798b99f6c3d41daf838ab1f8a505966ae1c`, 3,456 lines
  (header, results, summary). No parse failure. The log has 0 matches for `unpacked|restore|error|traceback`.
- Manifest inputs (header `manifest_sha256`): names `7f4e8c21...`, prototypes `b2909484...` and comments
  `596891df...` are unchanged from run 3; types.tsv `3ad5adc8...`, types.h `39864eaf...` and skipped `144a679c...`
  are new (T006b/T006c).
- Work copy after: sha256 `65120b34...8b9111`, mtime 10:03 (unchanged). Only the three `.i64` files are in the
  folder. Counts before = after: local types 788, user names 51,074, typed functions 453.

| Kind | Would write | Already | Refused | Refused % | Other |
| --- | ---: | ---: | ---: | ---: | --- |
| types | 87 (declare) | 3 | **91** | **50.3%** | |
| remove-label | 3 | | 0 | 0% | |
| names | 1,079 | | 0 | 0% | |
| prototypes | 919 | | 92 | 9.1% | |
| comments | 1,119 | | 0 | 0% | |
| conflict-names / conflict-prototypes | | | | | 7 / 54 reported, not written |

`already` types: `CPacket`, `MtObject`, `cSeedGameSvConnection`. 0 types would be defined.

### 2.1 Refusals (verified from the dump with jq)

| Step | check | count | named types |
| --- | --- | ---: | --- |
| types | `different-local-type` | 1 | `MtArray` |
| types | `embeds-refused-type` | 90 | all `MtTypedArray<...>`, each names only `MtArray` |
| prototypes | `uses-refused-type` | 92 | all name an `MtTypedArray<...>` |

The root record, from the dump:

    existing: size 20: ["",0,4,"base","MtObject"], mLength +4 4 uint32_t, mBufsiz +8 4, mAutoDelete +12 1, mpArray +16 4
    row:      size 20: ["baseclass_0",0,4,"base","unsigned __int8"], mLength, mBufsiz, mAutoDelete, gapD +13 3, mpArray +16 4

Cause (verified by reading the code and both revisions of `types.h`):

- At `d8c3df4301` (run 3), `types.h` had `MtObject baseclass_0; // +0x0 4 base MtObject`, and T007c's base rule
  accepted it as `already`.
- From `e49ae1b3416` (T006b) on, `MtObject` is `opaque declared` in `types.tsv`. So `transfer/render.py` line 51
  renders a base whose class is not transferred as `unsigned __int8 baseclass_0[4]; // ... base MtObject (not
  transferred)`.
- `apply_transfer.py` `member_equal` (lines 179-182) requires `ex["type"] == row.type` for a base member. The
  parser takes `row.type` from the C type (`unsigned __int8`), not from the class named in the comment. So the base
  of the existing `MtArray` (an unnamed base of type `MtObject`, present in the database before T007b) no longer
  compares equal, even though the size, every offset, and the non-gap member names agree.

The existing `MtArray` is in the pre-T007b database (local types 788 at the rollback point), not a T007b write.

### 2.2 What else the dry run shows (verified from the dump)

- `nUserSession::CPacket_S2C_CHANGE_JOB_RES` is `would-declare`, an opaque forward declaration with no layout.
  `0x80cf80` would get its name, prototype and comment (`would-set`; the DB prototype is now
  `int __thiscall(int this, CPacket *packet)`). Inferred: after a successful apply, its `this` would be an opaque
  pointer, as the brief expects.
- The 6 lea-only types (`CDataClanSearchResult`, `CDataGPShopLineupElementBase`, `CDataGameTimeBaseInfo`,
  `CDataMailInfo`, `CDataOrbGainExtendParam`, `CDataWorldInfo`) are `opaque declared` in `types.tsv`. `types.h`
  has `struct X;` for each, and the dry run reports each as `would-declare`. So after an apply they **would exist
  as forward declarations without members**. They would not be absent from the local types, so the brief's extra
  check 3 ("absent from the local types") would fail as worded. Inferred intent: "no layout" (no members). The
  coordinator should restate the check.
- If `MtArray` compared equal, the cascade would disappear: 90 `MtTypedArray<...>` defines and 92 prototypes
  (inferred: their only refusal names `MtArray`/`MtTypedArray`, but their own checks have not run). That gives
  types 87 declare + 90 define + 4 already = 181, and prototypes 1,011.

## 3. Not run

Apply, second apply, verify, PC re-extract with comparison, the T007b spot checks and the extra checks of step 3
(the opaque `0x80cf80`, an `MtTypedArray` member access by name, the lea-only types): **not run** (stop
condition). No `apply.jsonl`, `apply-2.jsonl`, `apply-verify.jsonl` or `pc-ida-applied.jsonl` exists for this run.
Step 4 (delete `...run3-T007b.i64`) was not done because the checks did not pass. The run-3 copy stays in place
until a re-apply passes.

## 4. Options for the coordinator (inferred, not decided here)

1. `apply_transfer.py`: for a row base rendered as a byte array, compare the existing base's type with the class
   named in the `base X (not transferred)` comment. Or accept an existing base of any type when the row's base
   class is not transferred and the offset and size match. The parser would need to keep the comment's class name.
2. T006 `render.py`: keep rendering a base by its class name (`MtObject baseclass_0;`) when that class is
   declared opaque and already exists in the database. The 4-byte opaque `MtObject` cannot be embedded by value
   unless the database has its definition, so option 1 is the safer fix (inferred).
3. Restate extra check 3 as "the 6 lea-only types are forward declarations with no members".
4. Then rerun T007e from step 2. The work copy equals the rollback copy (`65120b34...8b9111`); no new rollback
   is needed.

## 5. Files

| File | sha256 | state |
| --- | --- | --- |
| work copy `.i64` | `65120b34...8b9111` | = rollback copy, unwritten by this run |
| `...exe.before-T007b.i64` | `65120b34...8b9111` | unchanged |
| `...exe.run3-T007b.i64` | `f17d0745...07829` | kept (checks not passed) |
| `dumps/apply-dryrun.jsonl` | `e462226a...ae1c` | new |

`dumps/MANIFEST.tsv` was regenerated (`uv run python manifest.py`). Its rows follow the renames: the
`*.run3.jsonl` rows carry the hashes of the run-3 files they replace, and `apply-dryrun.jsonl` is new. The other
rows are unchanged. Log: `dumps/logs/apply-dryrun.log`.

## 6. Run 2 (after T007f `a56731c675a`): steps 2-7 done, every check passes

Base `3e4c418c574`, 2026-11-03 13:15-13:21 (WEST). Same work copy, same `idat.exe`, batch only. ida-mcp was not
used, and neither the original nor the accepted database was opened. `apply_transfer.py` sha256
`9dd8d3a9de197f2fbd2b619d0f253b76029812a3dcc16bd758e21597c9360ed0` (T007f; `script_version` 1). Manifest inputs
are the same as in run 1 (header `manifest_sha256`: types.tsv `3ad5adc8...`, types.h `39864eaf...`, names
`7f4e8c21...`, prototypes `b2909484...`, comments `596891df...`, skipped `144a679c...`). Header `input_sha256`
`f1c974d0...fa20`, `idb_path` under `ddon-data-007work`. The spot-check script confirms the database: 32-bit
exactly, image base `0x400000`. Addresses are VAs.

**Outcome: 0 refusals and 0 failures. The second apply finds every row `already`, and verify reports every row `ok`
with `counts_ok: true` and 1,011 of 1,011 decompilations ok. The re-extract shows that the changed names and
prototypes are exactly the written rows, both ways (1,079 / 1,011). The extra checks pass with check 3 as
restated. The run-3 copy was deleted. The rollback copy was kept.**

### 6.1 Start state (no new rollback)

Before the run: work copy `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` (equal to
`...exe.before-T007b.i64`), and `...exe.run3-T007b.i64` `f17d0745...07829`. Run 1's dry-run files were renamed:
`dumps/apply-dryrun.jsonl` became `apply-dryrun.e1.jsonl` (sha256 `e462226a...ae1c`), and
`dumps/logs/apply-dryrun.log` became `apply-dryrun.e1.log`.

### 6.2 Commands, counts and hashes

    "$IDAT" -A -L$T/dumps/logs/apply-dryrun.log   "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB                 # 13:16, rc 0, 10 s
    "$IDAT" -A -L$T/dumps/logs/apply.log          "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply.jsonl --apply" $DB                 # 13:17, rc 0, 16 s
    "$IDAT" -A -L$T/dumps/logs/apply-2.log        "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-2.jsonl --apply" $DB               # 13:17, rc 0, 14 s
    "$IDAT" -A -L$T/dumps/logs/apply-verify.log   "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-verify.jsonl --verify --apply-log $T/dumps/apply.jsonl" $DB  # 13:17, rc 0, 24 s
    "$IDAT" -A -L$T/dumps/logs/pc-ida-applied.log "-S$T/extract_ida.py $T/dumps/pc-ida-applied.jsonl pc" $DB                                       # 13:18, rc 0, 43 s
    "$IDAT" -A -L$T/dumps/logs/apply-spot-check.log "-S$SCRATCH/spot_e2.py" $DB                                                                   # 13:19, rc 0

Counts come from `jq -r 'select(.kind=="result") | [.step,.status] | @tsv' <dump> | sort | uniq -c`:

| Kind | dry run | apply | second apply | verify |
| --- | --- | --- | --- | --- |
| types (181) | 87 would-declare, 90 would-define, 4 already, **0 refused** | 87 declared, 90 defined, 4 already | 181 already | 181 ok |
| remove-label | 3 would-remove | 3 removed | 3 already | 3 ok |
| names | 1,079 would-set | 1,079 set | 1,079 already | 1,079 ok |
| prototypes | 1,011 would-set, **0 refused** | 1,011 set | 1,011 already | 1,011 ok |
| comments | 1,119 would-set | 1,119 set | 1,119 already | 1,119 ok |
| decompile | | | | 1,011 ok, 0 failures |
| conflict-names / -prototypes | 7 / 54 reported | same, not written | same | |
| `failed` | | **0** | 0 | 0 mismatch |

The 4 `already` types are `CPacket`, `MtObject`, `cSeedGameSvConnection` and **`MtArray`**. The T007f base rule
compares `MtArray`'s untransferred base by its class, so the database's base of type `MtObject` is kept (the
spot check prints `struct __cppobj MtArray : MtObject { uint32_t mLength; uint32_t mBufsiz; bool mAutoDelete;
MtObject **mpArray; }`). The run-1 cascade (91 types and 92 prototypes refused) is gone. The second apply wrote
0 undo records.

Verify counts record: before 788 / 51,074 / 453 (local types / user names / typed functions), applied delta
+177 / +1,074 / +1,011, expected = after = 965 / 52,148 / 1,464, `ok: true`. Run 3 had +182 local types. This
run's +177 equals 87 declared + 90 defined.

| Step | Work copy sha256 | bytes | mtime |
| --- | --- | ---: | --- |
| start, after the dry run (unchanged) | `65120b34...8b9111` | 111,886,983 | 10:03 |
| after the apply | `7f62aaef02764186df4976a9a13abddb68ca6439c4ea8fec268927a6677ab8c6` | 112,322,464 | 13:17 |
| after the second apply (re-saved by `qexit(0)`, 0 writes) | `be0cc624fdb38deaa646de2ecea04fbf8d5297d8d37cf164ca4a61310aee162f` | 112,370,180 | 13:17 |
| after verify, the extract and the spot check (each `DBFL_KILL`) | `be0cc624...162f` | 112,370,180 | 13:17 |

The hash changes on the second apply although it wrote nothing. Inferred: IDA re-saves and repacks the database
on `qexit(0)`. The dump records 0 writes and 0 undo records, and the later read-only runs leave the hash unchanged.

| Dump | sha256 | lines |
| --- | --- | ---: |
| `dumps/apply-dryrun.jsonl` | `5b7c0422ea2343ddee289a6ef1326f15ec21a56660cf045a00d75e6f2c7f6186` | 3,456 |
| `dumps/apply.jsonl` | `b1c4ce64e5becc05901ca8871d9ec99884e5b196ee04f5aee5870e643dd0acf0` | 6,845 |
| `dumps/apply-2.jsonl` | `c96ba930b07a4cadfb31b49ee5bf70190963b91565fb933ced13f4aab1f81bdc` | 3,456 |
| `dumps/apply-verify.jsonl` | `f3eb68c419027c3c63a388db9ef7427324ca66a30d82ea11c66a10b3f4e56794` | 4,407 |
| `dumps/pc-ida-applied.jsonl` (extract_ida v5) | `0d5ae8587d01f70f39e089d6ff5472de081b3dab9ea25a928b2ecaa180d1e913` | 8,914 |

Logs: `rg -ci "unpacked|restore|traceback"` finds 0 matches in each of the five run logs. After every run, only
the `.i64` files are in the work folder (no `.id0`/`.id1`/`.nam`/`.til`).

### 6.3 Re-extract and compare (step 6)

The comparison reuses run 3's `cmp_applied.py` (scratchpad, stdlib, unchanged; run with `uv run python -X utf8` from
`ida-transfer/`). The baseline `dumps/pc-ida.jsonl` is `4b307aee...61f0` (v4). The function records are 7,262
before and after, with the same VAs. The other record kinds are equal (1,041 table, 575 extern, 33 requester
sites, 1 missing root).

| | changed in dump | written rows | changed, not written | written, not changed | written outside dump scope |
| --- | ---: | ---: | ---: | ---: | ---: |
| names | 1,079 | 1,079 | 0 | 0 | 0 |
| prototypes | 1,011 | 1,011 | 0 | 0 | 0 |

Every changed name equals its `names.tsv` row. Every changed prototype equals its `decl` with the
`struct`/`union`/`enum ` keywords ignored (0 differences; 171 printed with `struct `). All 1,011 have
`prototype_user: true`. Other changed fields, none of them written rows: `annotations` in 1,448 functions,
`default_name` in 1,077, `ecx_read_before_write` in 356, `object_accesses` and `data_refs` in 5. These are the
same categories and counts as in run 3, except `annotations`: 1,448 here, where run 3 reported its parts as 1,119
comments, 23 lvars and 536 insn-comment functions. The `ecx_read_before_write` change keeps run 3's inferred cause
(the v4 to v5 extractor change).

### 6.4 Spot checks and extra checks (step 7)

Script `spot_e2.py` (scratchpad, read-only, ends with `DBFL_KILL`): `get_name`, `get_type`, `get_func_cmt`,
`ida_hexrays.decompile`, and for named types `tinfo_t.get_named_type`, `is_forward_decl`, `get_udt_nmembers`.
Output: `spot_e2.json`. All 11 functions decompile without error, and their arguments carry the row names.

The names, prototypes and comments are as in run 3 (§3.7 of `T007b-apply-run.md`) for `0x7c3450`, `0x7cb030`,
`0x7c4930`, `0x802de0`, `0x758810`, `0x76e5a0`, `0x823720`, `0x81def0` and `0x879860`. Each paired function's
comment starts `PS4 02020005: <name> (<mangled>); paired by <rule>.`, and each seed handler's starts with
`PC name from string at 0x...`. The pseudocode reads as in run 3: the sender writes `in_ScoutEntryID`, the
requester passes `maxHp` to `Send_C2S_CHARACTER_GOLDEN_REVIVE_REQ`, and the handlers have a typed `this`.

Extra checks (verified):

1. **`0x80cf80` and the CHANGE_JOB_RES handler `0x7de910` show no transferred layout.** `0x80cf80`
   `nUserSession::CPacket_S2C_CHANGE_JOB_RES::ReadPacket`, `int __thiscall(struct
   nUserSession::CPacket_S2C_CHANGE_JOB_RES *this, CPacket *pPacket)`. Every access is a raw offset now, with no
   member names:

        v3 = (_DWORD *)((char *)this + 16);
        if ( nPacket::Read_s32(pPacket, (int *)this + 4) == 0 ) return 0;
        if ( *v3 != 0 ) { *((_DWORD *)this + 5) = *v3; *((_BYTE *)this + 236) = 1; return 1; }
        ... nPacket::Read_CDataS2CCharacterEquipInfo_(pPacket, (struct MtTypedArray<CDataS2CCharacterEquipInfo> *)((char *)this + 96))
        ... nPacket::Read_CDataSetAcquirementParam_(pPacket, (struct MtTypedArray<CDataSetAcquirementParam> *)((char *)this + 116))
        *((_DWORD *)this + 3) = HIBYTE_w(pPacket); *((_BYTE *)this + 236) = 1;

   `0x7de910` `cSeedGameSvConnection::OnPacket_JOB_CHANGE_JOB_RES`, `int __thiscall(cSeedGameSvConnection *this,
   CPacket *pPacket)`, comment `PC name from string at 0x1bcf464. PS4 02020005:
   cSeedGameSvConnection::OnPacket_S2C_CHANGE_JOB_RES (...); paired by seed.` It allocates `0xF0` bytes and types
   the object as `struct nUserSession::CPacket_S2C_CHANGE_JOB_RES *v5`. It reads the result with
   `*((_DWORD *)v5 + 4)`, falling back to `+ 5`, also by raw offset.
2. **`MtTypedArray<...>` member access by name.** `0x758810` `nPacket::Read_CDataAchievementProgress_(CPacket
   *packet, struct MtTypedArray<CDataAchievementProgress> *ar)` contains `ar->mAutoDelete = true;`. The type is
   `struct __fixed(0x14) MtTypedArray<CDataAchievementProgress> : struct MtArray {}`, size 20, with 1 member (the
   base). The function's later accesses go through a copy cast to `unsigned int *` (`v2[2]`, `mBufsiz`), as in run 3.
3. **Restated: the 6 lea-only types and CHANGE_JOB_RES exist only as forward declarations without members.** All 7
   (`nUserSession::CPacket_S2C_CHANGE_JOB_RES`, `CDataClanSearchResult`, `CDataGPShopLineupElementBase`,
   `CDataGameTimeBaseInfo`, `CDataMailInfo`, `CDataOrbGainExtendParam`, `CDataWorldInfo`) exist with
   `is_forward_decl` true, are not udt (no members), and have size `BADSIZE`. One consequence differs from run 3:
   `0x76e5a0` `nPacket::Read_CDataMailInfo_(CPacket *packet, CDataMailInfo *d)` now decompiles to raw offsets
   (`(unsigned __int64 *)d + 1`, `(unsigned __int8 *)d + 16`, `(MtString *)d + 11`) where run 3 showed
   `d->m_ullId`. This is expected for an opaque type.

### 6.5 Files after run 2

| File | sha256 | state |
| --- | --- | --- |
| work copy `.i64` | `be0cc624...162f` | applied (run 2) |
| `...exe.before-T007b.i64` | `65120b34...8b9111` | kept (rollback point) |
| `...exe.run3-T007b.i64` | was `f17d0745...07829` | **deleted** after all checks passed (13:20) |

`dumps/MANIFEST.tsv` was regenerated with `uv run python manifest.py`. The diff against the copy taken before:
it adds `apply-dryrun.e1.jsonl` (run 1's hash, under the new name), and the new `apply-dryrun.jsonl`, `apply.jsonl`,
`apply-2.jsonl`, `apply-verify.jsonl` and `pc-ida-applied.jsonl`. No other row changed. New logs:
`dumps/logs/apply-dryrun.log`, `apply.log`, `apply-2.log`, `apply-verify.log`, `pc-ida-applied.log`,
`apply-spot-check.log`.
