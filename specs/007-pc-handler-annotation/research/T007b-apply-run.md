# 007 T007b: apply run (PC 03040008) - run 3 complete; run 1 stopped after the dry run, run 2 restored after the apply

Build PC 03040008, work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
(input sha256 `f1c974d0...fa20`, header `idb_path` confirmed under `ddon-data-007work`). First run base
`59bf8e3e9b3`, 2026-11-03 12:28-12:40 (WET); rerun base `4f9926d22e`, 2026-11-03 12:34-12:38 (WEST); run 3 base
`d8c3df4301`, 2026-11-03 12:48-12:55 (WEST). IDA work by `C:/Program Files/IDA Professional 9.5/idat.exe` batch
only; ida-mcp was not used. Addresses are VAs (image base `0x400000`, 32-bit).

**Run 3 outcome (after T007d `5362d5c45c`): steps 1-7 done, every check passes; the spot checks found one
contradicted layout.** The dry run is byte-identical to run 2's (0 refusals). Apply: 0 `failed` (types 182
written + 7 already, names 1,079, labels removed 3, prototypes 1,011, comments 1,119). Second apply: everything
`already`, no undo record. Verify: every row `ok`, counts `ok`, 1,011 of 1,011 decompilations `ok`. Re-extract:
the changed names and prototypes are exactly the written rows, both ways (1,079 / 1,011). The spot checks read
sensibly, except that the PC reader `0x80cf80` **contradicts** the transferred layout of
`nUserSession::CPacket_S2C_CHANGE_JOB_RES`: on PC its members after the header sit 0xc bytes later. The work copy
is now sha256 `f17d0745...7829`; the rollback copy is unchanged. Section "Run 3".

**Rerun outcome (after T007c `c91df1e373`): stopped at step 3, work copy restored.** The dry run is clean
(0 refusals in every kind). The apply writes every row, but 171 prototype read-backs come back `failed`. In
every one of them, IDA prints `struct ` in front of a type name that contains `::` or `<...>`, and the row's
text does not have it. The diagnostic batch shows the types resolve to the intended local types. The brief says
to restore on any `failed` row, so the rollback copy was copied back (sha256 `65120b34...8b9111` again). Steps
4-7 were not run. Section "Rerun".

**First-run outcome: stopped at step 2.** The dry run refuses 105 of 189 type rows (55.6%), above the brief's 10% stop
threshold. Steps 3-7 (apply, second apply, verify, re-extract, spot checks) were **not run**. The work copy was
not written; its sha256 is unchanged.

## First run (base 59bf8e3e9b3)

### 1. Rollback point

    sha256sum ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    cp -p ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64 ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64

| File | sha256 | bytes |
| --- | --- | --- |
| work copy `.i64` (before) | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 |
| `...exe.before-T007b.i64` | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 |

Equal: verified. The rollback copy stays in place for the rerun.

### 2. Dry run

    T=D:/ddon-data/research/03040008/ida-transfer
    idat -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # rc 0, 11 s

- Output `dumps/apply-dryrun.jsonl` (the rerun renamed it `dumps/apply-dryrun.run1.jsonl` and its log
  `logs/apply-dryrun.run1.log`): sha256 `bd500eb50458f63ad44ad6edb2bf09451a795890a968f8dc1735cf483f92fea7`,
  3,464 lines (header, 3,462 results, summary); row added to `dumps/MANIFEST.tsv` (`uv run python manifest.py`;
  the three dump rows unchanged).
- Manifest inputs (header `manifest_sha256`): names `7f4e8c21...`, prototypes `b2909484...`, comments `596891df...`,
  types.tsv `fdcf08f7...`, types.h `ddad9dfb...`, skipped `c17db87b...`. No parse failure.
- Work copy after: sha256 `65120b34...8b9111` (unchanged), mtime 10:03 (unchanged); log has no
  "unpacked"/"restore" prompt; no unpacked files beside the `.i64`.
- Counts before (header) = counts after (dry run): local types 788, user names 51,074, typed functions 453.

| Kind | Would write | Already | Refused | Refused % | Other |
| --- | ---: | ---: | ---: | ---: | --- |
| types | 80 (declare) | 4 | **105** | **55.6%** | |
| remove-label | 3 | | 0 | 0% | |
| names | 1,079 | | 0 | 0% | |
| prototypes | 912 | | 99 | 9.8% | |
| comments | 1,119 | | 0 | 0% | |
| conflict-names | | | | | 7 reported, not written |
| conflict-prototypes | | | | | 54 reported, not written |

`already` types: `CPacket`, `MtString`, `MtString::STRING`, `cSeedGameSvConnection`.

#### 2.1 Refusal reasons (verified from the dump)

| Step | check | count |
| --- | --- | ---: |
| types | `different-local-type` | 3 |
| types | `embeds-refused-type` | 102 |
| prototypes | `uses-refused-type` | 99 |

The three root refusals are local types that already exist in the work copy with the **same size and the same
member offsets and sizes**; only member names differ (`existing` vs `row`, from the dump):

| Type (types.tsv status) | Existing in DB | Row (types.h) | Difference |
| --- | --- | --- | --- |
| `MtObject` (accepted) | size 4: `_vptr$MtObject` +0 4 | size 4: `__vftable` +0 4 | vptr member name |
| `CPacketDataBase` (embedded) | size 4: `""` +0 4 | size 4: `baseclass_0` +0 4 | base member unnamed in DB |
| `MtArray` (embedded) | size 20: `""` +0 4, `mLength` +4 4, `mBufsiz` +8 4, `mAutoDelete` +12 1, `mpArray` +16 4 | size 20: `baseclass_0` +0 4, same four, gap `gapD` +13 3 | base member unnamed in DB (gap not compared) |

The cascade (`embeds-refused-type` names the refused type each struct embeds; a struct can name several):
`MtArray` 92, `CPacketDataBase` 10, `CDataCharacterName` 2, five `MtTypedArray<...>` and
`CDataCommunityCharacterBaseInfo`, `CDataCharacterJobData` 1 each. All 99 prototype refusals name a refused
type (mostly `MtTypedArray<CDataX>` element readers, e.g. `0x758100` `MtTypedArray<CDataAbilityLevelParam>`,
plus `nUserSession::CPacket_S2C_CHANGE_JOB_RES`). So all 204 refusals trace back to these three name-only
differences (verified: every `embeds`/`uses` record lists only types in the refused set).

The apply script behaves as README § "Apply script" specifies (equal layout = size and non-gap members'
name/offset/size; different -> refused unless `types.tsv` status is `replace`); none of the three rows is
`replace`. This is not a script fault.

### 3. Not run

Apply, second apply (idempotence), verify, PC re-extract and comparison, spot checks: **not run** (stop
condition). No `apply.jsonl`, `apply-2.jsonl`, `apply-verify.jsonl`, `pc-ida-applied.jsonl` exist. The `_Ida`
adapter's write path (udt build, `create_typedef`, tinfo serialize) is therefore still untested on a real
database; the read path (precheck, counts, type/name/prototype lookups) ran without error.

### 4. Options for the coordinator (inferred, not decided here)

1. In T006, treat the three as equal-layout types: mark them `replace`, or emit the existing member names
   (`_vptr$MtObject`, unnamed base) so the comparison finds `already`. With `already` the cascade disappears;
   expected dry run then about 185 types written/already and 1,011 prototypes (inferred: the 102 embedding
   structs and 99 prototypes were refused only for these types, but their own checks have not run).
2. Or change `apply_transfer.py`'s layout equality to ignore member names for a vptr at +0 and an unnamed or
   `baseclass_<off>` base member, keeping offsets and sizes strict.
3. `replace` would overwrite the DB's existing `MtObject`/`MtArray`/`CPacketDataBase`, whose origin
   (earlier annotation or IDA) was not checked here; option 1 with the existing names or option 2 leaves them.

Rerun T007b from step 2 after the fix; the rollback copy `...exe.before-T007b.i64` (sha256 above) is in place.

## Rerun (base 4f9926d22e, after T007c c91df1e373)

Same work copy, same `idat.exe`, batch only; ida-mcp not used. `apply_transfer.py` script version 1 as of
`4f9926d22e` (with T007c's `same_layout`). Manifest inputs unchanged: the header `manifest_sha256` values equal
the first run's (names `7f4e8c21...`, prototypes `b2909484...`, comments `596891df...`, types.tsv `fdcf08f7...`,
types.h `ddad9dfb...`, skipped `c17db87b...`).

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"

### R1. Rollback point (not copied again)

    sha256sum ddon-data-007work/*.i64

`2022_01_29_DDO_DUMP_FIX.exe.i64` and `...exe.before-T007b.i64`: both
`65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111`, 111,886,983 bytes, mtime 10:03. Verified.

### R2. Dry run (clean)

    mv dumps/apply-dryrun.jsonl dumps/apply-dryrun.run1.jsonl; mv dumps/logs/apply-dryrun.log dumps/logs/apply-dryrun.run1.log
    "$IDAT" -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # rc 0, 10 s

- `dumps/apply-dryrun.jsonl`: sha256 `5d25d04d14304d7f170f203c03c6ec1badf78adbed9a0b7572eb071357332523`, 3,464
  lines (header, 3,462 results, summary). No parse failure. The log has no error or traceback and no
  "unpacked"/"restore" prompt.
- Work copy after: sha256 `65120b34...8b9111`, mtime 10:03 (unchanged). Counts before = after: local types 788,
  user names 51,074, typed functions 453.

| Kind | Would write | Already | Refused | Other |
| --- | ---: | ---: | ---: | --- |
| types | 182 (80 declare, 102 define) | 7 | 0 | |
| remove-label | 3 | | 0 | |
| names | 1,079 (1,077 `set`, 2 `correct`) | | 0 | |
| prototypes | 1,011 | | 0 | |
| comments | 1,119 | | 0 | |
| conflict-names / conflict-prototypes | | | | 7 / 54 reported, not written |

`already` types: `CPacket`, `MtString`, `MtString::STRING` and `cSeedGameSvConnection`, as in the first run,
plus `MtObject`, `CPacketDataBase` and `MtArray`. Under T007c's rule the three first-run refusals now count as
equal. The 2 `correct` names are `0x7c61f0` (DB
`cSeedGameSvConnection::OnPacket_S2C_BAZAAR_GET_EXHIBIT_POSSIBLE_NUM_RES`) and `0x7c6510` (DB
`...::OnPacket_S2C_BAZAAR_GET_ITEM_PRICE_LIMIT_RES`). The first run's inferred expectation (about 185 types,
1,011 prototypes) is now verified as 189 types and 1,011 prototypes.

### R3. Apply: 171 prototype read-back failures, work copy restored

    "$IDAT" -A -L$T/dumps/logs/apply.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply.jsonl --apply" $DB
    # rc 0, 14 s

- `dumps/apply.jsonl`: sha256 `1addfb6c5fd8c1431aaebdc78706cb9a9389b3fc4e27d0d4c1dcb0393697eb99`, 6,858 lines
  (header, 3,462 results, 3,394 undo records, summary). No `.tmp` file is left. The log has no error or
  traceback and no "unpacked"/"restore" prompt; it ends with "Flushing buffers, please wait...ok" (saved).
- Work copy after: sha256 `7d92c177c7a7d844c1eee11b0c77453559e791dbc912af841b74a02d533c9dfe`, 112,332,011 bytes,
  mtime 12:35; no unpacked files beside it.
- Counts before -> after (header / summary): local types 788 -> 970, +182 (80 declared plus 102 defined). Names
  51,074 -> 52,148, +1,074 (1,077 `set` on default names minus 3 removed labels). Typed functions 453 -> 1,464,
  +1,011 (every prototype was applied, the failed rows included).

| Kind | written | already | refused | failed |
| --- | ---: | ---: | ---: | ---: |
| types | 182 (80 declared, 102 defined) | 7 | 0 | 0 |
| remove-label | 3 | | 0 | 0 |
| names | 1,079 | | 0 | 0 |
| prototypes | 840 | | 0 | **171** |
| comments | 1,119 | | 0 | 0 |

**The failing calls.** All 171 records have `check: read-back` and `applied: true`. So
`apply_tinfo(ea, tif, TINFO_DEFINITE)` returned true, and then `idc.get_type(ea)` differed from the row under
`norm`, which only collapses whitespace (`apply_transfer.py` line 271 and lines 548-553). No exception and no
other error text. Examples from the dump:

| VA | `db` (`idc.get_type` read-back) | `row` (`prototypes.tsv` `decl`) |
| --- | --- | --- |
| `0x758100` | `int __cdecl(CPacket *packet, struct MtTypedArray<CDataAbilityLevelParam> *ar)` | `int __cdecl(CPacket *packet, MtTypedArray<CDataAbilityLevelParam> *ar)` |
| `0x7ffaf0` | `int __thiscall(struct nUserSession::CPacket_S2C_AREA_RANK_UP_RES *this, CPacket *pPacket)` | the same without `struct ` |
| `0x87caa0` | `bool __thiscall(cNetGameServer *this, int slotNo, struct nNet::stPawnFeedback *feedback)` | the same without `struct ` |

Full list: `jq -c 'select(.status=="failed")' dumps/apply.jsonl` (from `0x758100` to `0x87caa0`).

Classification (verified with jq over `dumps/apply.jsonl` and `manifest/transfer/prototypes.tsv`):

- In all 171 records, `db` with `struct ` deleted and whitespace collapsed equals `row` exactly. Each `db`
  contains `struct ` exactly once. The names it precedes: 101 `MtTypedArray<...>`, 69
  `nUserSession::CPacket_S2C_*_RES`, 1 `nNet::stPawnFeedback`.
- `prototypes.tsv` has 171 rows whose `decl` contains `::` or `<`, and they are exactly the failed rows. None
  of the 840 `set` rows contains either.
- `parse_prototype` patches these rows through `_ref`: `create_typedef(til, name, BTF_STRUCT, True)`, then
  `create_ptr`. When the name is not a plain C identifier, IDA prints the reference with a `struct ` keyword.
  Plain names print without it: `cNetGameServer *`, for example, is a forward declaration (ordinal 799) and has
  no `struct `. (Inferred from these read-backs; the IDA printer source was not read.)

Before the restore, a read-only diagnostic batch ran on the applied copy (`diag.py` in the scratchpad
`C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/`; it
ends with `DBFL_KILL` and `qexit(0)`). The copy's sha256 afterwards was still `7d92c177...9dfe`, mtime 12:35.
Results for 4 failed VAs:

| VA | argument | pointed type resolves to | local type |
| --- | --- | --- | --- |
| `0x758100` | `ar` | `MtTypedArray<CDataAbilityLevelParam>`, udt, size 20 | ordinal 878, size 20 |
| `0x7ffaf0` | `this` | `nUserSession::CPacket_S2C_AREA_RANK_UP_RES`, forward decl | ordinal 802 |
| `0x80d170` | `this` | `nUserSession::CPacket_S2C_CHANGE_PAWN_JOB_RES`, forward decl | ordinal 804 |
| `0x87caa0` | `feedback` | `nNet::stPawnFeedback`, forward decl | ordinal 800 |

All four decompiled without error, with the transferred name, the argument names and the PS4 comment, for
example:

    // PS4 02020005: nPacket::Read<CDataAbilityLevelParam> (_ZN7nPacket4ReadI22CDataAbilityLevelParamEEiR7CPacketR12MtTypedArrayIT_E); paired by element-reader.
    int __cdecl nPacket::Read_CDataAbilityLevelParam_(CPacket *packet, struct MtTypedArray<CDataAbilityLevelParam> *ar)

The writes are the intended types: verified for these 4, and inferred for the other 167 because they follow the
same pattern. What fails is the read-back comparison, which does not accept IDA's `struct ` keyword as equal.
The brief says: "if any write `failed` ... restore ... do not edit the script". So:

    cp -p ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64 ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    sha256sum ddon-data-007work/*.i64     # 12:37

Both files: `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111`, 111,886,983 bytes, mtime 10:03.
Restore verified. `dumps/apply.jsonl` therefore records a database state that no longer exists. Its undo
records were not used, because copying the file back was the rollback.

### R4. Not run

Steps 4-7 were **not run** because the stop condition fired: second apply, verify, PC re-extract with
comparison, spot checks. No `apply-2.jsonl`, `apply-verify.jsonl` or `pc-ida-applied.jsonl` exists.

The `_Ida` write path did run on a real database for the first time. The udt build, `create_forward_decl`,
`create_typedef`, `set_named_type`, the name and comment writes and the tinfo serialize for undo raised no
errors. Their read-backs matched: types 182, names 1,082 (including the 3 removed labels), comments 1,119,
prototypes 840.

`dumps/MANIFEST.tsv` was regenerated (`uv run python manifest.py`). It has rows for `apply-dryrun.jsonl`
(rerun), `apply-dryrun.run1.jsonl` (first run, `bd500eb5...`) and `apply.jsonl`; the other rows are unchanged.

### R5. Options for the coordinator (inferred, not decided here)

1. Fix the prototype comparison in `apply_transfer.py`: drop a `struct `/`union `/`enum ` keyword before a type
   name before comparing, or compare the applied tinfo with the parsed one (`tinfo_t.compare_with`, or
   serialized equality) instead of the printed text. The fix has to reach three places that use the same
   `norm` text comparison (read from the code; not run):
   - the read-back (line 550);
   - the second `--apply`'s `already` check (line 518), where these 171 rows would be user-typed but unequal
     and therefore `refused` as `user-prototype` (line 528);
   - `--verify` (line 678), which would report them as `mismatch`.
2. Or have T006 write `struct ` into `decl` for `::`/`<...>` names. That changes the manifest and its hashes.
3. Then rerun T007b from step 3; the dry run does not depend on this comparison. The rollback copy is in place
   and equals the work copy.

## Run 3 (base d8c3df4301, after T007d 5362d5c45c)

Same work copy, same `idat.exe`, batch only; ida-mcp not used. `apply_transfer.py` as of `d8c3df4301` (last
change `9ab79f9303d`, sha256 `a8a84254...9c88`; the header `script_version` is still `1`), with T007d's tinfo
comparison. Manifest inputs unchanged: the header `manifest_sha256` values equal those of runs 1 and 2 (names
`7f4e8c21...`, prototypes `b2909484...`, comments `596891df...`, types.tsv `fdcf08f7...`, types.h `ddad9dfb...`,
skipped `c17db87b...`).

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"

Run 2's dumps were kept by renaming them: `dumps/apply-dryrun.run2.jsonl`, `dumps/apply.run2.jsonl`,
`dumps/logs/apply-dryrun.run2.log`, `dumps/logs/apply.run2.log`.

### 3.1 Rollback point (not copied again)

    sha256sum ddon-data-007work/*.i64      # 12:48

Work copy and `...exe.before-T007b.i64`: both `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111`,
111,886,983 bytes, mtime 10:03. Verified.

### 3.2 Dry run

    "$IDAT" -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # rc 0, 17 s

`dumps/apply-dryrun.jsonl`: sha256 `5d25d04d...2523`, 3,464 lines, **byte-identical to run 2's**
(`apply-dryrun.run2.jsonl`). The counts are the same: types 80 declare + 102 define + 7 already, remove-label 3,
names 1,079, prototypes 1,011, comments 1,119, and 7 / 54 conflicts reported; 0 refusals. The work copy is
unchanged (`65120b34...8b9111`, mtime 10:03). The log has no error, traceback or "unpacked"/"restore" text.

### 3.3 Apply

    "$IDAT" -A -L$T/dumps/logs/apply.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply.jsonl --apply" $DB
    # 12:49, rc 0, 28 s

- `dumps/apply.jsonl`: sha256 `75274827594578b2392454727b24f0938e339f02b77d778036f54e8dde9d0d2d`, 6,858 lines
  (header, 3,462 results, 3,394 undo records, summary). No `.tmp` file is left. The log ends with the summary
  line and "Flushing buffers, please wait...ok"; `rg -c -i 'unpacked|restore packed'` finds 0 matches.
- Work copy after: sha256 `0fe5e0a67bef23d4d473396edcaa91e6dbc39e0553abae30994c6b16903ab8da`, 112,332,011 bytes,
  mtime 12:49. Only the two `.i64` files are in the folder.
- Counts before -> after: local types 788 -> 970 (+182), names 51,074 -> 52,148 (+1,074, that is 1,077 `set` on
  default names minus 3 removed labels), typed functions 453 -> 1,464 (+1,011).

| Kind | written | already | refused | failed |
| --- | ---: | ---: | ---: | ---: |
| types | 182 (80 declared, 102 defined) | 7 | 0 | 0 |
| remove-label | 3 | | 0 | 0 |
| names | 1,079 | | 0 | 0 |
| prototypes | 1,011 | | 0 | **0** |
| comments | 1,119 | | 0 | 0 |
| conflict-names / conflict-prototypes | | | | 7 / 54 reported, not written |

The 171 rows that failed in run 2 now pass the read-back (for example `0x758100`, `status: set`). Their printed
type still carries `struct ` (171 applied prototypes contain it, see 3.6), and T007d's tinfo comparison accepts
it. No restore was needed.

### 3.4 Second apply (idempotence)

    "$IDAT" -A -L$T/dumps/logs/apply-2.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-2.jsonl --apply" $DB
    # 12:50, rc 0, 10 s

`dumps/apply-2.jsonl`: sha256 `12d1f10f...3f9c`, 3,464 lines, **no undo record**. Every row is `already`: types
189, remove-label 3, names 1,079, prototypes 1,011, comments 1,119 (and 7 / 54 conflicts reported). Counts after:
970 / 52,148 / 1,464, unchanged. Idempotence verified.

`idc.qexit(0)` still re-saved the file: sha256 `f17d0745ac939e99f6389d85bb17ddc9eb97b7bc6a806eae2374aefbaf907829`,
112,375,929 bytes (+43,918), mtime 12:50. Inferred: IDA repacks the database on every save (session and
autoanalysis state); the dump and the counts show that no row changed. The log has no "unpacked"/"restore" text,
and no unpacked files are left.

### 3.5 Verify

    "$IDAT" -A -L$T/dumps/logs/apply-verify.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-verify.jsonl --verify --apply-log $T/dumps/apply.jsonl" $DB
    # 12:50, rc 0, 26 s

`dumps/apply-verify.jsonl`: sha256 `c8dbcdba...2884`, 4,415 lines. The summary has `counts_ok: true` and these
results: types 189 ok, remove-label 3 ok, names 1,079 ok, prototypes 1,011 ok, comments 1,119 ok, **decompile
1,011 ok, 0 failures**. No row is `mismatch`. The counts record: before 788 / 51,074 / 453, applied delta +182 /
+1,074 / +1,011, expected = after = 970 / 52,148 / 1,464. The work copy is unchanged afterwards
(`f17d0745...7829`; the run ends with `DBFL_KILL`).

### 3.6 Re-extract PC and compare

    "$IDAT" -A -L$T/dumps/logs/pc-ida-applied.log "-S$T/extract_ida.py $T/dumps/pc-ida-applied.jsonl pc" $DB
    # 12:51, rc 0, 41 s

`dumps/pc-ida-applied.jsonl`: sha256 `551d6f41...fc37`, 8,914 lines, `extract_ida` script version **5**. The
baseline `dumps/pc-ida.jsonl` (sha256 `4b307aee...61f0`) is version 4. Record counts equal the baseline's: 7,262
functions at the same VAs, 1,041 table, 575 extern, 33 requester sites, 1 missing root. The work copy is unchanged
afterwards (`f17d0745...7829`).

The comparison script is `cmp_applied.py` in the scratchpad (Python stdlib). Its key is the function `va`; the
written rows are the `status: set` records of `dumps/apply.jsonl`; the expected values come from
`manifest/transfer/{names,prototypes}.tsv`.

| | changed in dump | written rows | changed, not written | written, not changed | written outside dump scope |
| --- | ---: | ---: | ---: | ---: | ---: |
| names | 1,079 | 1,079 | 0 | 0 | 0 |
| prototypes (`prototype`, `prototype_user`) | 1,011 | 1,011 | 0 | 0 | 0 |

- Every changed name equals its `names.tsv` row. Every changed prototype equals its `prototypes.tsv` `decl` once
  the `struct`/`union`/`enum ` keywords are deleted and whitespace is collapsed (0 differences; 171 contain
  `struct `). All 1,011 have `prototype_user: true`. Verified both ways.
- Other fields also differ. They are not written rows; they are listed so that they are not mistaken for writes:
  - `annotations.function_comment` in 1,119 functions, exactly the comment rows. `annotations.lvars` in 23, all
    with a new prototype. `default_name` in 1,077, the `set` names on default names.
  - `annotations.insn_comments` in 536 functions, all callers of a reprototyped function. These are IDA's
    automatic argument comments at call sites (`0x86f045` `in_PawnID`, `0x86f049` `this`), a consequence of the
    prototypes.
  - `data_refs`/`object_accesses` in 5 functions: new `0xFF000000...` ids (inferred: IDA struct-member type ids
    from the applied types) and more accesses counted in memcpy/memset.
  - `ecx_read_before_write` goes from true to false in 356 functions (6,214 -> 5,858 true); only 20 of them are
    reprototyped. Inferred cause: extractor v5 decodes memory operands from `op_t` (`a5131eff533`), and the
    baseline is v4. This run does not separate the two effects; a v5 extract of the pre-apply copy was not run.

### 3.7 Spot checks

The spot checks are read-only batch scripts in the scratchpad
(`C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/`):
`spot3.py` and `spot3b.py`. They call `auto_wait`, `get_name`, `get_type`, `get_func_cmt`,
`ida_hexrays.decompile` and the disassembly printer, then end with `DBFL_KILL` and `qexit`. Logs:
`dumps/logs/apply-spot-check.log` and `apply-spot-check-b.log`. Database confirmed: `idb_path` under
`ddon-data-007work`, `inf_is_32bit_exactly` true, image base `0x400000`. The work copy is unchanged afterwards
(`f17d0745...7829`, mtime 12:50). All 10 functions decompiled without error, and their arguments carry the row
names.

| Role | VA | Name | Prototype (IDA print) |
| --- | --- | --- | --- |
| handler (seed) | `0x7c3450` | `cSeedGameSvConnection::OnPacket_ACHIEVEMENT_ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_RES` | `int __thiscall(cSeedGameSvConnection *this, CPacket *pPacket)` |
| handler (seed) | `0x7cb030` | `cSeedGameSvConnection::OnPacket_CLAN_CLAN_GET_JOIN_REQUESTED_LIST_RES` | same |
| handler (tier0, no pair) | `0x7c4930` | `cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_CHARACTER_INFO_RES` | `int __thiscall(cSeedGameSvConnection *this, void *packet)` |
| reader (struct) | `0x80cf80` | `nUserSession::CPacket_S2C_CHANGE_JOB_RES::ReadPacket` | `int __thiscall(struct nUserSession::CPacket_S2C_CHANGE_JOB_RES *this, CPacket *pPacket)` |
| reader (opaque) | `0x802de0` | `nUserSession::CPacket_S2C_CLAN_BASE_GET_INFO_RES::ReadPacket` | `int __thiscall(struct nUserSession::CPacket_S2C_CLAN_BASE_GET_INFO_RES *this, CPacket *pPacket)` |
| element reader (template) | `0x758810` | `nPacket::Read_CDataAchievementProgress_` | `int __cdecl(CPacket *packet, struct MtTypedArray<CDataAchievementProgress> *ar)` |
| element reader (struct) | `0x76e5a0` | `nPacket::Read_CDataMailInfo_` | `int __cdecl(CPacket *packet, CDataMailInfo *d)` |
| sender | `0x823720` | `cSeedGameSvConnection::Send_C2S_CLAN_SCOUT_ENTRY_INVITE_REQ` | `int __thiscall(cSeedGameSvConnection *this, unsigned int in_ScoutEntryID)` |
| sender | `0x81def0` | `cSeedGameSvConnection::Send_C2S_ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_REQ` | `int __thiscall(cSeedGameSvConnection *this)` |
| requester | `0x879860` | `cNetGameServer::reqCharacterGoldenRevive` | `bool __thiscall(cNetGameServer *this, unsigned int maxHp)` |

Comments: every paired function starts with `// PS4 02020005: <name> (<mangled>); paired by <rule>.`. The seed
handlers start with `// PC name from string at 0x... . PS4 02020005: ...`, the tier0 handler with only
`// PC name from string at 0x1bd5c10.`

Pseudocode excerpts (sliced):

    // 0x76e5a0 element reader, transferred struct: reads sensibly, members at the right places
    int __cdecl nPacket::Read_CDataMailInfo_(CPacket *packet, CDataMailInfo *d)
    {
      return nPacket::Read_u64(packet, &d->m_ullId) != 0
          && nPacket::Read_u8(packet, &d->m_ucState) != 0
          && nPacket::Read_u8(packet, &d->m_ucItemState) != 0
          && sub_75ECF0(packet, (int)&d->m_BaseInfo)
          && nPacket::Read_MtString(packet, &d->m_wstrSenderName) != 0
          && nPacket::Read_MtString(packet, &d->m_wstrMailText) != 0
          && nPacket::Read_s64(packet, (unsigned __int64 *)&d->m_llSenderDate) != 0;
    }

    // 0x758810 element reader, MtTypedArray<...>: MtArray members used consistently (mAutoDelete +0xc, mBufsiz +8)
    int __cdecl nPacket::Read_CDataAchievementProgress_(CPacket *packet, struct MtTypedArray<CDataAchievementProgress> *ar)
      v2 = (unsigned int *)ar;
      ar->mAutoDelete = true;
      ...
      u32 = nPacket::Read_u32(packet, (unsigned int *)&ar);
      if ( v2[2] < (unsigned int)ar ) sub_85DD70(v2, (unsigned int)ar);

    // 0x823720 sender: CPacket local typed, argument named
    if ( nUserSession::CPacket::WritePacket(&packet, 0x1Fu, 24, 1u, -1)
      && nPacket::Write_u32(&packet, in_ScoutEntryID) != 0 )
      cSeedServerConnection::Send((cSeedServerConnection *)this, (char *)packet.m_pReader, packet.m_pWriter - packet.m_pReader);

    // 0x879860 requester: calls the transferred sender with the named argument
    || cSeedGameSvConnection::Send_C2S_CHARACTER_GOLDEN_REVIVE_REQ(*((cSeedGameSvConnection **)this + 2675), maxHp) == 0 )

    // 0x7c4930 tier0 handler: named, this typed; its reader is still sub_800200
    sub_785F30(v5);
    if ( sub_800200((int)v5, (CPacket *)packet) != 0 )
      cSeedGameSvConnection::callOnPacketFunc((MtObject *)this->mpManager, 734,
        (int)aCseedgamesvcon_4 /* "cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_CHARACTER_INFO_RES" */, ...);

    // 0x7c3450 seed handler: this typed; the packet object pointer sits in the opaque part of cSeedGameSvConnection
    v3 = *(void (__thiscall ****)(_DWORD, int))&this->opaque140[788];

#### 3.7.1 Contradicted: the `nUserSession::CPacket_S2C_CHANGE_JOB_RES` layout (types.tsv `accepted`, "no contradiction")

The reader `0x80cf80` decompiles with the struct on `this`, but the members do not fit:

    p_m_ucJob = &this->m_CharacterJobData.m_ucJob;
    if ( nPacket::Read_s32(pPacket, (int *)&this->m_CharacterJobData.m_ucJob) == 0 ) return 0;
    if ( *(_DWORD *)p_m_ucJob != 0 ) { this->m_CharacterJobData.m_unExp = ...; this->m_LearnNormalSkillParamList.mAutoDelete = true; return 1; }
    ... nPacket::Read_CDataS2CCharacterEquipInfo_(pPacket, (struct MtTypedArray<CDataS2CCharacterEquipInfo> *)&this->m_CharacterEquipList.mAutoDelete)
    ... nPacket::Read_CDataSetAcquirementParam_(pPacket, (struct MtTypedArray<CDataSetAcquirementParam> *)&this->m_AddItemList.mAutoDelete)

Raw offsets from the disassembly (verified), against `types.h` lines 744-763:

| PC code (`esi` = `this`) | offset | transferred member at that offset |
| --- | --- | --- |
| `0x80cf89` `Read_s32(this+0x10)`; if non-zero, `[esi+14h]` = it, `[esi+0ECh]` = 1, return 1 | +0x10, +0x14, +0xEC | `m_CharacterJobData.m_ucJob` (+0xc+4), `.m_unExp`, `m_LearnNormalSkillParamList.mAutoDelete` |
| `0x80cfbc` `Read_s32(this+0x14)` | +0x14 | `m_CharacterJobData.m_unExp` |
| `0x80cfcd` `sub_75C770(this+0x18)` | +0x18 | inside `m_CharacterJobData` (member at +0xc) |
| `0x80cfde` `Read_CDataS2CCharacterEquipInfo_(this+0x60)` | +0x60 | `m_CharacterEquipList` +0xc (member at +0x54) |
| `0x80cfef` / `0x80d000` `Read_CDataSetAcquirementParam_(this+0x74 / +0x88)` | +0x74, +0x88 | `m_AddItemList` / `m_BagItemList` +0xc (`MtTypedArray<CDataItemList>`) |
| `0x80d014` `sub_76CD60(this+0x9C)`, `0x80d02c` `Read_CDataEquipJobItem_(this+0xB0)`, `0x80d044` +0xC4, `0x80d05c` +0xD0 | | further arrays |
| `0x80d07b` `[esi+0Ch]` = `HIBYTE_w(packet)`; `0x80d084` `[esi+0ECh]` = 1 | +0xC, +0xEC | the `m_CharacterJobData` base; `m_LearnNormalSkillParamList.mAutoDelete` (the transferred `m_bIsReceived` is at +0x114) |

The opaque reader `0x802de0` (`CPacket_S2C_CLAN_BASE_GET_INFO_RES`) has the same shape: `Read_s32(this+0x10)`;
if non-zero, store it at +0x14 and set the flag byte at +0xD4; otherwise `Read_s32(this+0x14)` and members from
+0x1C. So on PC 03040008 these S2C packet objects keep a result/error pair at +0x10/+0x14. CHANGE_JOB_RES's first
payload member is at +0x18, 0xc bytes after the transferred `m_CharacterJobData` (+0xc). Every array starts 0xc
after its transferred offset, and the received flag is at +0xEC, not +0x114. At +0x74/+0x88 the element type also
differs from PS4: the PC code calls `CDataSetAcquirementParam` readers where PS4 declares
`MtTypedArray<CDataItemList>`.

Status: the offsets are **verified** (disassembly above), so the transferred layout is **contradicted** for PC
03040008. The field identities on PC are **inferred** and not established here (which of +0x10/+0x14 is
`m_nResult` or `m_usError`, and what +0xC holds). T006 accepted the type ("14 checked accesses, no contradiction").
Inferred from `types.tsv` `evidence_vas` (`0x80cf89` to `0x80d02c`) against these offsets: each access falls
inside some member, and the check did not catch accesses at member start + 0xc. Beyond the two element readers
above, the other written struct readers were not checked. The types embedded only through this packet
(`CDataCharacterJobData`, `MtTypedArray<CDataItemList>`, `MtTypedArray<CDataLearnNormalSkillParam>`; types.tsv
"checked through it") rest on the same evidence.

The brief's stop conditions (a write `failed`, a read-back disagreement) did not fire, so the database was not
restored. Options for the coordinator (not decided here): undo this type alone (drop or correct the row in
T006, then `--undo` or the rollback copy and a re-apply), or keep it and fix the layout in a later T006 pass
whose PC-offset check requires pointer-argument accesses to land on member starts.

### 3.8 Hashes and files

| Step | Work copy sha256 | bytes | mtime |
| --- | --- | ---: | --- |
| start / after the dry run | `65120b34...8b9111` | 111,886,983 | 10:03 |
| after the apply | `0fe5e0a6...ab8da` | 112,332,011 | 12:49 |
| after the second apply, verify, extract, spot checks | `f17d0745...07829` | 112,375,929 | 12:50 |
| rollback copy `...before-T007b.i64` (unchanged) | `65120b34...8b9111` | 111,886,983 | 10:03 |

`dumps/MANIFEST.tsv` was regenerated (`uv run python manifest.py`). New rows: `apply.jsonl` (run 3),
`apply-2.jsonl`, `apply-verify.jsonl`, `pc-ida-applied.jsonl` (extract_ida 5), `apply-dryrun.run2.jsonl`,
`apply.run2.jsonl`. `apply-dryrun.jsonl` (the same hash as run 2) and the other rows are unchanged. Logs:
`dumps/logs/apply-dryrun.log`, `apply.log`, `apply-2.log`, `apply-verify.log`, `pc-ida-applied.log`,
`apply-spot-check.log`, `apply-spot-check-b.log`. No write-run log contains "unpacked" or "restore", and no
unpacked files are left beside the `.i64`. Not run: a v5 extract of the pre-apply database, which would separate
the extractor-version drift in `ecx_read_before_write` from the apply's effects.
