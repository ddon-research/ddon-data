# 007 T007e: roll back and re-apply (PC 03040008): stopped at step 2 (dry run), work copy clean

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
